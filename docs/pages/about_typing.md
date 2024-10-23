---
layout: page
title: About Typing
permalink: /about_typing/
nav_order: 102
---

<h1 style="font-weight: bold">About Typing</h1>

XFP works a lot with a stricter typing universe than plain Python. However similar convention repeat along the library. Since relying on a signature to understand behavior is a core objective, it is important to understand the meaning behind each convention.

## Reading a signature

Let's use the signature of flat_map_right as an example

```python
    ...
    def flat_map_right(self, f: Callable[[X], E]) -> "Xresult[Y, E]"
    ...
```

The noticeable feature here is a fully typed argument list, as well as return type. However to achieve readability and Python interoperability, it makes uses of TypeVar with sightly different meaning than the method's behavior : 
- `X` : defined class-level, it **always** represents the principal type of the collection (the collection type for Xlist, Xiter, ... and the biased side of Xresult, ...).
- `Y` : when defined, it represents byproduct of functions (the opposite side of Xresult). If a third type is one day necessary, the by-byproduct would be `Z`, and so on.
- `E` : this type is trickier. Defined globally as an external TypeVar, it is an alias for `Any`, and is used to keep track for an obfuscated type in a method. For example here, the strictest signature would be `def flat_map_right[Z, I](self, f: Callable[[X], Xresult[I, Z]]) -> "Xresult[Y | I, Z]"`. The complexity of the full signature raises concern with readability, so we choose to erase the output of the callable f. By extension, it erase the product of the Xresult too, which makes an output of `E`.

{: .warning }
**Type Erasure**  
While improving readability, the `E` type makes place for some unnoticed errors, see [this](/python-fp/functional_programming/) for more information.
