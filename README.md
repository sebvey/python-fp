# zfp library prject

A custom functional style library for python

# HOW TO CONTRIBUTE

## Setup
- clone the repo
- install poetry
- install compatible python version (from 3.11), eg. `pyenv install 3.12.3`
- install the project : `poetry install`
- set up the git hook scripts (for black): `pre-commit install` 

-> poetry installs xfp package in editable mode, so that xfp is available as a package from anywhere and editable.  

## Black
Black is used as python formatter. If setup done as above, black formats all commited files before commit.  
To manually format a file : `black path/to/file`  
All files, from project root dir : `black .`  

Info on Black IDE integration [here](https://black.readthedocs.io/en/stable/integrations/editors.html)

We should configure output python versions ... possibliy done automatically from pyproject.toml...  
https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html  

## Pre-commit
More info : https://pre-commit.com/

## CI/CD (Github)
- github action `pytest-action` is setup to run pytest on each push
- **TODO** : protect main branch to block merge from a branch which last commit has failed actions
- **TODO** : auto deploy to PYPI on merge to main branch

# HOW TO PUBLISH TO PYPI

By now, pypi credentials (token) is configured locally with :  
`poetry config pypi-token.pypi <token>``

To publish locally (from given branch) :  
`poetry publish`
