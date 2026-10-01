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

lint: install
	uv run flake8 $(PY_FILES)
	uv run mypy $(PY_FILES) \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs
		--check-untyped-defs

.PHONY: install run debug clean lint lint_strict