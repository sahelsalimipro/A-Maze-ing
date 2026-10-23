.PHONY: install, run, debug, clean, lint, lint-strict

install:
	echo " Installing --- Done"

run:
	python a_maze_ing.py ".env"

debug:
	python -m pdb a_maze_ing.py ".env"


clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	find . -type d \( -name ".mypy_cache" -o -name ".pytest_cache" -o -name ".ruff_cache" -o -name ".ipynb_checkpoints" \) -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	rm -rf .tox .nox .coverage htmlcov build dist .hypothesis

lint:
	-flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	-flake8 .
	mypy . --strict
