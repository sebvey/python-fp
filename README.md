# xfp library prject

A custom functional style library for python.  
Github repository [HERE](https://github.com/sebvey/python-fp/)

# HOW TO CONTRIBUTE

## Setup
- clone the repo
- install poetry
- install compatible python version (from 3.11), eg. `pyenv install 3.12.3`
- install the project : `poetry install`
- set up the git hook scripts (for black): `pre-commit install` 

-> poetry installs xfp package in editable mode, so that xfp is available as a package from anywhere and editable.  

## Linter / formatter = ruff
Ruff is hooked on pre-commit as linter and formatter.  
More here : https://github.com/astral-sh/ruff

## Pre-commit
More info : https://pre-commit.com/

## CI/CD (Github)

- Main branch : no pushes, only merges from branches that pass tests
- github action `pytest-action` is setup to run pytest on each push
- **TODO** : auto deploy to PyPI

# HOW TO PUBLISH TO PYPI

By now, pypi credentials (token) have to be configured locally with :  
`poetry config pypi-token.pypi <token>`

To publish locally (from given branch) :  
`poetry publish`
