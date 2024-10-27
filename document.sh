#!/bin/bash

MARKDOWN_DOCS_PATH="docs/source"
LANGUAGE="English"
TARGET_REPO_PATH="$(pwd)"

cd /home/tesla2000/PassionProjects/RepoAgent
.venv/bin/python repo_agent/main.py run --markdown-docs-path "$MARKDOWN_DOCS_PATH" --language "$LANGUAGE" --target-repo-path "$TARGET_REPO_PATH" --ignore-list .venv

cd $TARGET_REPO_PATH
sphinx-apidoc -o docs/source src/ --private
git add docs/source
python3 _add_markdowns.py
