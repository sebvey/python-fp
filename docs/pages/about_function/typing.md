---
layout: page
title: Typing
parent: Functional programming in Python
permalink: /typing/
nav_order: 2
---

<h1 style="font-weight: bold">Typing</h1>

XFP works a lot with a stricter typing universe than plain Python. However similar convention repeat along the library. Since relying on a signature to understand behavior is a core objective, it is important to understand the meaning behind each convention.

## Reading a signature

Let's use the signature of flat_map_right of [Xresult](/python-fp/results/) as an example

```python
    ...
    def flat_map_right[T, U](self, f: "F1[[X], Xresult[T, U]]") -> "Xresult[Y, Never] | Xresult[T, U]":
    ...
```

The noticeable feature here is a fully typed argument list, as well as return type. Moreover, XFP specific types bears additional, implicit meaning common in all the library :
- `X` : defined class-level, it **always** represents the principal type of the collection (the collection type for Xlist, Xiter, ... and the biased side of Xresult, ...).
- `Y` : when defined, it represents byproduct of functions (the opposite side of Xresult). If a third type is one day necessary, the by-byproduct would be `Z`, and so on.
- `T` : As a type parameter of a method, it defines an external principal type (i.e. the product of collection given as parameter).
- `U` : As a type parameter of a method, it defines an external byproduct.
- `F1` : Strictly an alias for Callable, however more readable and claiming this is the lowest level function you can get (i.e. takes a value, returns a value).
- `Xresult[Y, Never]`: when working with Xresult, a channel typed `Never`, `None` or any type of `Exception` means respectively a projection on the other side, an optional value, or a tried value

### Interpretation

Those meanings provide a strong, interpretable signature. Here it reads as :  
- method in Xeffect : A method working on an Xeffect
- `f: "F1[[X], Xresult[T, U]]"`: 
  - `[X]` : transforming the main path of the effect
  - `Xresult` : through an effectful transformation (warning, it may break)
- `Xresult[Y, Never] | Xresult[T, U]` : 
  - `Xresult[Y, Never]` : returning either self (if it is a LEFT, therefore right value is unused)
  - `Xresult[T, U]` : or the resulting value of the transformation (if it is a RIGHT)

{: .for-short :}
_A method working on a Xeffect, transforming the main path of the effect, doing either nothing if it was a LEFT or returning the result of the transformation otherwise.
Warning, it may break._
