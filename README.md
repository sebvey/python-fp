# XFP

[![PyPI version](https://badge.fury.io/py/xfp.svg)](https://badge.fury.io/py/xfp)
[![Coverage Status](https://coveralls.io/repos/github/sebvey/python-fp/badge.svg?branch=dev)](https://coveralls.io/github/sebvey/python-fp?branch=dev)

XFP is a python library allowing functional syntax with python collections.  
It enables dot notation on lists and iterators, and provides a way to functionally handle effects through values.
Its objectives is to add functional tools to the language (in opposition to making it functional), deeper than what the language evolutions proposes today (ie with its recent pattern matching and lambda functions).  

Github repository [HERE](https://github.com/sebvey/python-fp/)

# WHY

While python provides today some tools from functional languages (such as map, filter, ...), it fails as making its syntax functional-friendly. For example, multiple mapping/filtering requires a lot of intermediate values with few addition to code readability or robustess. Moreover some paradigms are missing to fully benefits from monadic behavior (map/flat_map/filter/foreach/...).  

The goal is to :
- add functional syntax to make functional python code edible
- add tools to complete the functionalities provided by python
- respect python strengthes : time to market, readability, ...

In order to achieve all of this, we propose a functional API adapted for python, taking into account its strengthes and weaknesses to enrich the language without twisting it too much.  

# QUICK START

xfp is plublished on PyPI [HERE](https://pypi.org/project/xfp/), easy to install with your package manager.

## How to run the demos
Some demos are provided in the `demo` folder. Each one is in a separate
subfolder.  

For simplicity :
- main code is in the `main.py` file
- eventual modules are in the same folder and used in `main.py` with relative imports

**To run the demos (here the xlist one):**
- make sure xfp is installed on your python environment (eg `cd python-fp && pip install .`)
- Run the demo from the root of the repo :`python -m demo.xiter.main`

## How to use in your project

### Collections

To use XFP on a collection, starts with creating a new Xlist :
```python
from xfp import Xlist, Xiter
xlist = Xlist([1, 2, 3])
# or xiter for the lazy iterator version. Functionalities differ a bit however
xiter = Xiter([1, 2, 3])
```

You can then start applying operations on the list, either through anonymous functions or defined ones.  
The  preconised style is to write one operation by line using the '()' operator :

```python
from xfp import Xlist

def under_eight(x: int) -> bool:
    return x < 8

(
    Xlist([1, 2, 3])
        .map(lambda x: x * x)                     # Xlist([1, 4, 9])
        .filter(under_eight)                      # Xlist([1, 4])
        .map(lambda x: f"this is a number : {x}") # Xlist(["this is a number : 1", "this is a number : 4"])
        .foreach(print)                           # prints each element of the list, return None
)
```

### XEffect

Functional behaviors requires proper encapsulation of 'not a value' meaning (for example, None or raise Exception).  
Those ecapsulations are modelised in xfp through the Xeffect class. It basically encapsulates a union type under two pathways, either LEFT or RIGHT, in a container. Think of this container as a 'list with one element'. Its API is homogene with the collection one.
```python
from xfp import Xeffect

r1 = Xeffect(1, XFXBranch.RIGHT)
r2 = Xeffect(3, XFXBranch.LEFT)

(
    r1
        .map_right(lambda x: x + 3)                        # Xeffect.right(4)
        .flat_map_right(lambda x: r2.map(lambda y: x + y)) # Xeffect.left(7)
        .filter_left(lambda x: x < 5)                      # Xeffect.right(XeffectError(...)) 
)
```

### XEither, XTry, XOpt

You can add more semantic to your effects by making use of the proxy types `XEither`, `XTry`, `XOpt`, respectively indicating "a formal union type", "something that can crash", "the presence or absence of an element".  
Those types resolves as an Xeffect, but can be used by themselves in pattern matching, and provide tooling revolving around their semantics. Example of XTry :

```python
from xfp import XTry

def should_raise(x):
    if x > 10:
        raise Exception("too much")
    else:
        return x

r1 = XTry.from_unsafe(lambda: should_raise(15)) # Xeffect.left(Exception("too much"))
r2 = XTry.from_unsafe(lambda: should_raise(8))  # Xeffect.right(8)

# a decorator is provided to automatically convert your functions
@XTry.safed
def safed_function(x):
    return should_raise(x)

r3: Xeffect[Exception, Int] = safed_function(15) # Xeffect.left(Exception("too much"))
r4: Xeffect[Exception, Int] = safed_function(8)  # Xeffect.right(8)

# Constructors are also available
r5: Xeffect[Exception, Int] = Xeffect.Success(3)

# You can pattern match an expression depending on its pathway
match r3:
    case XTry.Success(value):
        print(value)
    case XTry.Failure(exception):
        print(f"Something went wrong : {e}")
```

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
