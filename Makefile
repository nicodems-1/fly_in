MAIN = main
ARGS= ?=

install:
	uv sync 

run: install
	uv run python -m $(MAIN) $(ARGS)

debug: install
	uv pdbg python $(MAIN) $(ARGS)

clean:
	@echo "Cleaning up Python files"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

PY_FILES = main.py \
           parser.py \
           drone_fleet_handler.py \
           path_finder.py \
           load_map.py \
           drone_visual.py \
           colors_available.py \
           models.py

lint: install
	uv run flake8 $(PY_FILES)
	uv run mypy $(PY_FILES) \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

.PHONY: install run debug clean lint lint_strict