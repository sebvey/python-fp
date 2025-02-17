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
    def flat_map_right[T, U](self, f: "F1[[X], Xresult[T, U]]") -> "Xresult[Y | T, U]":
    ...
```

The noticeable feature here is a fully typed argument list, as well as return type. Moreover, XFP specific types bears additional, implicit meaning common in all the library :
- `X` : defined class-level, it **always** represents the principal type of the collection (the collection type for Xlist, Xiter, ... and the biased side of Xresult, ...).
- `Y` : when defined, it represents byproduct of functions (the opposite side of Xresult). If a third type is one day necessary, the by-byproduct would be `Z`, and so on.
- `F1` : Strictly an alias for Callable, however more readable and claiming this is the lowest level function you can get (i.e. takes a value, returns a value).
- `Y | T`: when working with union types of the same XFP type, the reduced form is always used. We can retrieve the raw result type by developping it. Since the factorized form represents a broarder type range than the developped one, we also need to add some of our knowledge. In this case :
  - We recognize the `Xresult[T, U]` in the return type that is also present in `f` return type.
  - We recognize `Xresult[Y, ???]` that represents the original left-side of the effect.
  - The developped form should therefore look like `Xresult[Y, TBD] | Xresult[T, U]`, where `TBD` must be a subtype of `U` to be compatible with the factorized form.
  - We know for sure two subtypes of `U` : itself (`U`) and `Never` (subtype of everything).
  - We discriminate by trying to provide interpretation for both cases. Here `Xresult[Y, U]` needs a transformation from `X` to `U` to be pertinent (which we don't have), while `Xresult[Y, Never]` is the type of an always LEFT side, unconditionnally.
  - Therefore the developped type is `Xresult[Y, Never] | Xresult[T, U]`

### Interpretation

Those meanings provide a strong, interpretable signature. Here it reads as :  
- method in Xeffect : A method working on an Xeffect
- `f: "F1[[X], Xresult[T, U]]"`: 
  - `[X]` : transforming the main path of the effect
  - `Xresult` : through an effectful transformation (warning, it may break)
- `Xresult[Y | T, U]` : 
  - `Xresult[Y, Never]` : returning either self (if it is a LEFT, therefore right value is unused)
  - `Xresult[T, U]` : or the resulting value of the transformation (if it is a RIGHT)

{: .for-short :}
_A method working on a Xeffect, transforming the main path of the effect, doing either nothing if it was a LEFT or returning the result of the transformation otherwise.
Warning, it may break._
