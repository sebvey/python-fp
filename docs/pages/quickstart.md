---
layout: page
title: Quick Start
permalink: /quickstart/
nav_order: 1
---

<h1 style="font-weight: bold">Quick Start</h1>

<h2>Install Xfp</h2>

You can install Xfp from PyPI via:
```shell
pip install --upgrade xfp
```

and then start using it in your python code : 

## Use with Collections

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
    .map(lambda x: x * x)                      # Xlist([1, 4, 9])
    .filter(under_eight)                       # Xlist([1, 4])
    .map(lambda x: f"this is a number : {x}")  # Xlist(["this is a number : 1", "this is a number : 4"])
    .foreach(print)                            # prints each element of the list, return None
)
```

## Side-effects handling

Functional behaviors requires proper encapsulation of 'not a value' meaning (for example, None or raise Exception).  
Those ecapsulations are modelised in xfp through the Xresult class. It basically encapsulates a union type under two pathways, either LEFT or RIGHT, in a container. Think of this container as a 'list with one element'. Its API is homogene with the collection one.
```python
from xfp import Xresult, XRBranch

r1 = Xresult(1, XRBranch.RIGHT)
r2 = Xresult(3, XRBranch.LEFT)

(
    r1
    .map_right(lambda x: x + 3)                        # XRBranch.RIGHT : 4
    .flat_map_right(lambda x: r2.map(lambda y: x + y)) # XRBranch.LEFT : 3
    .filter_left(lambda x: x > 5)                      # XRBranch.RIGHT : XresultError(...)
)
```

## Results chaining

You will often have to deal with multiple effects at once. To avoid the vanilla triangle of doom that would cause such dealing, xfp provides a convenient way to process them altogether.  
Let's illustrate it with a mock use case. A table computing and writing from three different sources : 

```python
from xfp import Xresult

def load_table(table_name: str) -> Xresult[Exception, DataFrame]:
    pass


def write_table(table_name: str, table: DataFrame) -> Xresult[Exception, None]:
    pass

def process(t1: DataFrame, t2: DataFrame, t3: DataFrame) -> DataFrame:
    pass

# 'Vanilla' xfp processing

load_table('db1.tb1').flat_map(
    lambda t1: load_table('db2.tb2').flat_map(
        lambda t2:load_table('db3.tb3').flat_map(
            lambda t3: write_table('db1.tb4', process(t1, t2, t3))
        )
    )
)

# Xfp result chaining

Xresult.fors(lambda:
    [
        write_table('db1.tb4', process(t1, t2, t3))
        for t1, t2, t3
        in zip(
            load_table('db1.tb1'),
            load_table('db2.tb2'),
            load_table('db3.tb3')
        )
    ])

```

## Quality of life

### Util functions

In functional programming, the operation consisting in transforming the function f in g (see below) is called curryfiction : 
```python
from xfp import Xlist
def f(i: int, j: str) -> Xlist[str]:
    pass

def g(i: int) -> Callable[[str], Xlist[str]]:
    def inner(j: str) -> Xlist[str]:
        pass
    return inner
```

While the `g` syntax is often useful (for example to prepare functions to use in a map operation), the writing of such function may be tedious.
XFP comes with a convenient decorator `curry` to infer the g function from the f one:

```python
from xfp import Xlist
from xfp.functions import curry2

# the effective signature of f becomes def f(i: int) -> Callable[[str], Xlist[str]]
@curry2
def f(i: int, j: str) -> Xlist[str]:
    return i * j

# notice the usage of only one parameter in f
(
    Xlist(["a", "b", "c"])
    .flat_map(f(3))
    .foreach(print)
)
```

### Xeither, Xtry, Xopt

You can add more semantic to your results by making use of the proxy types `Xeither`, `Xtry`, `Xopt`, respectively indicating "a formal union type", "something that can crash", "the presence or absence of an element".  
Those types resolves as an Xresult, but can be used by themselves in pattern matching, and provide tooling revolving around their semantics. Example of Xtry :

```python
from xfp import Xtry, Xresult

def should_raise(x):
    if x > 10:
        raise Exception("too much")
    else:
        return x

r1 = Xtry.from_unsafe(lambda: should_raise(15)) # Xtry.Failure(Exception("too much"))
r2 = Xtry.from_unsafe(lambda: should_raise(8))  # Xtry.Success(8)

# a decorator is provided to automatically convert your functions
@Xtry.safed
def safed_function(x):
    return should_raise(x)

r3: Xresult[Exception, int] = safed_function(15) # Xtry.Failure(Exception("too much"))
r4: Xresult[Exception, int] = safed_function(8)  # Xtry.Success(8)

# Constructors are also available
r5: Xresult[Exception, int] = Xtry.Success(3)

# You can pattern match an expression depending on its pathway
match r3:
    case Xtry.Success(value):
        print(value)
    case Xtry.Failure(exception):
        print(f"Something went wrong : {exception}")
```
