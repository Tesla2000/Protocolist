setup: poetry git_init git_add precommit_install

precommit_install:
	pre-commit install --hook-type pre-commit --hook-type pre-push
	pre-commit autoupdate

git_init:
	git init

git_add:
	git add .
	git commit -m "initial commit"

poetry:
	poetry config virtualenvs.in-project true
	poetry install

.PHONY: setup
