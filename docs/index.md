---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

<h1 style="font-weight: bold">XFP</h1>

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
[![Coverage Status](https://coveralls.io/repos/github/sebvey/python-fp/badge.svg?branch=dev)](https://coveralls.io/github/sebvey/python-fp?branch=dev)
[![PyPI version](https://badge.fury.io/py/xfp.svg)](https://badge.fury.io/py/xfp)

Since Python 3.0 `map`, `filter` & co (but more accurately even since Python 2 list comprehension), new versions of the language keep appending more and more functional elements, last in date being Generics, Union typing or Pattern Matching.  
However although functional programming in its roughest form is possible in Python, it fails in our opinion to keep itself nice and readable.
```python
# Look this awful little chunk of code, how cute it is <3

from functools import reduce

initial_value = ["oh", "look", "an", "array", "to", "process", "!"]
camel_cased = map(lambda chain: str(chain[0].upper()) + chain[1:], initial_value)
only_long_word = filter(lambda x: len(x) > 2, camel_cased)
output = reduce(lambda x, y: x + " " + y, only_long_word)

assert output == "Look Array Process"
```

This project aims to soften the functional syntax already existing within the language, and go even further by enabling more functional concepts. 
