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
Black is used as python formatter. If setup done as above, black formats all new commited files before commit.  
To manually format a file : `black path/to/file`  
All files, from project root dir : `black .`  

Info on Black IDE integration [here](https://black.readthedocs.io/en/stable/integrations/editors.html)

## Pre-commit
More info : https://pre-commit.com/

## TODOs
We should configure output python versions ...
TODO : possibliy done automatically from pyproject.toml...  
https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html  

# HOW TO PUBLISH TO PYPI

By now, pypi credentials (token) is configured locally with :  
`poetry config pypi-token.pypi <token>``

To publish locally (from given branch) :  
`poetry publish`
