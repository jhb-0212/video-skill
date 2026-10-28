# 域8：编排入口（make run EP=EP001 一条命令跑全程）
# 依赖：06-scripts/ 下的脚本，无需额外安装

EP ?= EP001
ENGINE ?= comfyui
DATA := ../05-data-center
SCRIPTS := .
PY := python

.PHONY: help run validate prompts check test lint dry-run clean

help:
	@echo "用法："
	@echo "  make run EP=EP001             跑整条管线（校验→提示词→编译校验→质检）"
	@echo "  make dry-run EP=EP001         只校验不出图"
	@echo "  make validate                数据校验（bible + storyboard + assets + engines）"
	@echo "  make prompts EP=EP001        只生成提示词"
	@echo "  make test                    跑测试"
	@echo "  make lint                    ruff lint"
	@echo "  make clean                   清理 out 产物"

run:
	$(PY) pipeline_runner.py --episode $(EP) --engine $(ENGINE)

dry-run:
	$(PY) pipeline_runner.py --episode $(EP) --engine $(ENGINE) --dry-run

validate:
	$(PY) validate_data.py all $(DATA)

prompts:
	$(PY) storyboard_to_prompts.py $(DATA)/episodes/$(EP)_storyboard.csv $(DATA)/bible $(EP) --engine $(ENGINE) --episode $(EP) --out-dir ./out

check:
	$(PY) check_assets.py $(DATA)/episodes/$(EP)_assets.csv $(DATA)/bible $(DATA)/versions --profile $(DATA)/quality-profile.json --out-dir ./out

test:
	$(PY) run_tests.py

lint:
	ruff check .

clean:
	rm -rf out/*_prompts.txt out/*_prompts.json out/*_batch.json
