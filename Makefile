MAIN = main.py
ARGS ?=

PY_FILES = main.py \
           parser.py \
           drone_fleet_handler.py \
           path_finder.py \
           load_map.py \
           drone_visual.py \
           colors_available.py \
           models.py

install:
	uv sync

run:
	uv run python $(MAIN) $(ARGS)

debug:
	uv run -m pdb $(MAIN) $(ARGS)

lint:
	uv run flake8 $(PY_FILES)
	uv run mypy $(PY_FILES) \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

clean:
	@echo "Cleaning up Python files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +

.PHONY: install run debug clean lint