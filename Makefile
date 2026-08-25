MAIN = src.main
OUTPUT = data/output


install:
	uv sync 

run: install
	uv run python -m $(MAIN)

debug: install
	uv pdbg python $(MAIN)

clean:
	@echo "Cleaning up Python files"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint: install
	uv run flake8 src ;\
	uv run mypy src \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

.PHONY: install run debug clean lint lint_strict