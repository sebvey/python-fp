# xfp library project

A custom functional style library for python.  
Github repository [HERE](https://github.com/sebvey/python-fp/)

# HOW TO USE
xfp is plublished on PyPI, easy to install with your package manager.

# HOW TO RUN THE DEMOS
Some demos are provided in the `demo` folder. Each one is in a separate
subfolder.  

For simplicity :
- main code is in the `main.py` file
- eventual modules are in the same folder and used in `main.py` with relative imports

**To run the demos (here the xlist one):**
- make sure xfp is installed on your python environment (eg `pip install xfp`)
- from the demo folder of the repo :`python -m xiter.main`

# HOW TO CONTRIBUTE

## Setup
- clone the repo
- install poetry
- install compatible python version (from 3.12), eg. `pyenv install 3.12.4`
- install the project : `poetry install`
- set up the git hook scripts (linter / formatter): `pre-commit install` 

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
`poetry build && poetry publish`
