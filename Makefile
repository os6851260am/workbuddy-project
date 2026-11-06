.PHONY: help check serve clean

help:
	@echo "AutoSeminar-Agent 指令列表:"
	@echo "  make check      - 质检当前生成的 seminar_pack 目录"
	@echo "  make serve      - 本地启动轻量服务器预览教具网页 (端口 8080)"
	@echo "  make clean      - 清除生成的临时教学包"

check:
	python3 tools/validate_pack.py seminar_pack

serve:
	@if [ -d "seminar_pack" ]; then \
		echo "正在启动本地教学教具预览: http://localhost:8080/interactive_poll.html"; \
		cd seminar_pack && python3 -m http.server 8080; \
	else \
		echo "错误: 未找到 seminar_pack 目录，请先运行 Agent 生成产物。"; \
	fi

clean:
	rm -rf seminar_pack
