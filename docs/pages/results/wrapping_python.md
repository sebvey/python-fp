---
layout: page
title: Wrapping Python
parent: Effects
permalink: /results/wrapping_python
nav_order: 2
---

<h1 style="font-weight: bold">Wrapping Python</h1>

Going from the imperative paradigm of procedures and raising Exception (among other effects results) to the functional "handling in a value" style can be tedious,
both to lift results into Xresult and then to process multiple Xresult alltogether. XFP ensures a smooth interface between plain Python and functional Python.

## Xopt lifting

XFP provides a simple and straightforward method to infer the branch of an optional value while creating a result.
```python
from xfp import Xopt, Xresult

python_optional: None | int = None
maybe: Xresult[None, int] = Xopt.from_optional(python_optional)
```

The `from_optional` constructor allows automatic result creation, which will be a LEFT when the python optional is None and a RIGHT otherwise.

## Xresults lifting

### Xtry

Xtry provides two ways of switching from functions that raises to functions that returns Xresult. You will use either one of them depending on if you are : 
1. Integrating with a third-party API :  

    ```python
    import pandas as pd
    from xfp import Xtry, Xresult

    tried_df: Xresult[Exception, pd.DataFrame] = Xtry.from_unsafe(lambda: pd.read_csv("may_break_file"))
    ```

2. Dealing with legacy code written imperative-style :  

    ```python
    from xfp import Xtry, Xresult

    @Xtry.safed
    def that_can_raise(i: int) -> str:
        if i > 0:
            return str(i)
        else:
            raise Exception("an Exception")

    result: Xresult[Exception, str] = that_can_raise(3)
    ```

the `Xtry.from_unsafe` feature relies on the unparametrized lambda to lazily evaluate the code given to it. It allows to delegate its execution to the `from_unsafe` wrapper, which ensures catching any non fatal exception that can be thrown.  
The `Xtry.safed` decorator, on the other side, automatically wrap its subject inside a `from_unsafe` on call, effectivelly changing its signature to an Xresult.

{: .note }
While `Xtry.safed` can look appealing by removing some boilerplate on your handcrafted function, the best practice remains to explicitely returns `Xtry.Success` and `Xtry.Failure` to eliminate unnecessary confusion over both the code readability and the function signature.
