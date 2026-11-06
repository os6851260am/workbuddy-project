#!/usr/bin/env python3
"""
AutoSeminar Artifact Validator
用于静态检测 Agent 交付的 seminar_pack 是否满足教学契约与离线运行约束。
"""

import os
import sys
from pathlib import Path


def validate(pack_dir: str) -> bool:
    target = Path(pack_dir)
    errors = []
    warnings = []

    if not target.exists() or not target.is_dir():
        print(f"❌ [路径错误] 目录 '{pack_dir}' 不存在")
        return False

    # 1. 核心教学文件完整性检查
    required_files = [
        "README_TEACHER.md",
        "case_background.md",
        "interactive_poll.html",
    ]
    for rf in required_files:
        file_path = target / rf
        if not file_path.exists():
            errors.append(f"缺失核心文件: {rf}")
        elif file_path.stat().st_size == 0:
            errors.append(f"文件内容为空: {rf}")

    # 2. 多方对抗角色卡检查
    roles_dir = target / "roles"
    if not roles_dir.exists() or not roles_dir.is_dir():
        errors.append("缺失角色卡目录: roles/")
    else:
        role_cards = list(roles_dir.glob("*.md"))
        if len(role_cards) < 3:
            errors.append(f"角色卡数量不足: 预期至少 3 个立场角色，实际检测到 {len(role_cards)} 个")
        else:
            for card in role_cards:
                if card.stat().st_size < 50:
                    warnings.append(f"角色卡 '{card.name}' 内容过短，可能缺乏充分抗辩细节")

    # 3. 教具脱机契约与组件检查
    html_file = target / "interactive_poll.html"
    if html_file.exists():
        try:
            content = html_file.read_text(encoding="utf-8")

            # 约束 1: 零外部网络依赖（脱机运行）
            if "http://" in content or "https://" in content:
                errors.append(
                    "违反离线运行契约: HTML 中包含外部网络资源链接 (http/https)，脱机环境可能无法渲染"
                )

            # 约束 2: 必须包含责任分配滑块
            if 'type="range"' not in content and "type='range'" not in content:
                errors.append("缺失核心组件: 未检测到用于责任分配的 HTML 滑块 (<input type=\"range\">)")

            # 约束 3: 必须包含基础 JS 逻辑
            if "<script>" not in content or "</script>" not in content:
                errors.append("缺失交互逻辑: HTML 中未包含内嵌 <script> 逻辑")

        except Exception as e:
            errors.append(f"读取 HTML 文件异常: {str(e)}")

    # 4. 输出质检报告
    print("=" * 60)
    print(f"  AutoSeminar Agent 交付成果质检报告: {pack_dir}")
    print("=" * 60)

    if warnings:
        for w in warnings:
            print(f"⚠️  [警告] {w}")

    if errors:
        for err in errors:
            print(f"❌ [未通过] {err}")
        print("\n=> 质检结果: 失败（产物未满足执行规范，需 Agent 修正）\n")
        return False

    print("✅ 结构完整性通过（所有 Markdown 与角色卡就绪）")
    print("✅ 离线脱机契约通过（零外部 CDN 依赖，纯原生运行）")
    print("✅ 交互教具组件检测通过（包含滑动条及交互脚本）")
    print("\n=> 质检结果: 全部合格，可直接投入课堂使用！\n")
    return True


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "seminar_pack"
    success = validate(target_dir)
    sys.exit(0 if success else 1)
