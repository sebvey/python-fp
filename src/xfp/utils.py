from inspect import signature
from functools import partial
from typing import TypeVar, ParamSpec, cast, Concatenate, Callable, Any

# fmt: off
from xfp.stubs import F0, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22
# fmt: on
A = TypeVar("A")
P = ParamSpec("P")
T = TypeVar("T")
Self = TypeVar("Self")

# Element type alias
type E = Any
type Unused = None


def id[E](e: E) -> E:
    return e


def _curry(f: Callable[Concatenate[A, P], T]) -> Callable[[A], Any]:
    if len(signature(f).parameters) == 1:
        return cast(Callable[[A], T], f)
    else:

        def g(x: A) -> Callable:
            return curry(cast(Callable, partial(f, x)))

        return g


def _curry_method(f: Callable[Concatenate[Self, A, P], T]) -> Callable[[Self, A], Any]:
    if len(signature(f).parameters) == 2:
        return cast(Callable[[Self, A], T], f)
    else:

        def g(self: Self, x: A) -> Callable:
            return curry(cast(Callable, partial(f, self, x)))

        return g


# fmt: off
def curry(f: Callable[Concatenate[A, P], T]) -> Callable[[A], Any]: return _curry(f)
def curry0[Out](f: F1[[], Out])                                                                                                                                                                                                                                                      -> F0[Out]: return f
def curry1[In1, Out](f: F1[[In1], Out])                                                                                                                                                                                                                                              -> F1[[In1], Out]: return _curry(f)
def curry2[In1, In2, Out](f: F1[[In1, In2], Out])                                                                                                                                                                                                                                    -> F2[[In1], [In2], Out]: return _curry(f)
def curry3[In1, In2, In3, Out](f: F1[[In1, In2, In3], Out])                                                                                                                                                                                                                          -> F3[[In1], [In2], [In3], Out]: return _curry(f)
def curry4[In1, In2, In3, In4, Out](f: F1[[In1, In2, In3, In4], Out])                                                                                                                                                                                                                -> F4[[In1], [In2], [In3], [In4], Out]: return _curry(f)
def curry5[In1, In2, In3, In4, In5, Out](f: F1[[In1, In2, In3, In4, In5], Out])                                                                                                                                                                                                      -> F5[[In1], [In2], [In3], [In4], [In5], Out]: return _curry(f)
def curry6[In1, In2, In3, In4, In5, In6, Out](f: F1[[In1, In2, In3, In4, In5, In6], Out])                                                                                                                                                                                            -> F6[[In1], [In2], [In3], [In4], [In5], [In6], Out]: return _curry(f)
def curry7[In1, In2, In3, In4, In5, In6, In7, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7], Out])                                                                                                                                                                                  -> F7[[In1], [In2], [In3], [In4], [In5], [In6], [In7], Out]: return _curry(f)
def curry8[In1, In2, In3, In4, In5, In6, In7, In8, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8], Out])                                                                                                                                                                        -> F8[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], Out]: return _curry(f)
def curry9[In1, In2, In3, In4, In5, In6, In7, In8, In9, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9], Out])                                                                                                                                                              -> F9[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], Out]: return _curry(f)
def curry10[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10], Out])                                                                                                                                                 -> F10[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], Out]: return _curry(f)
def curry11[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11], Out])                                                                                                                                     -> F11[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], Out]: return _curry(f)
def curry12[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12], Out])                                                                                                                         -> F12[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], Out]: return _curry(f)
def curry13[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13], Out])                                                                                                             -> F13[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], Out]: return _curry(f)
def curry14[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14], Out])                                                                                                 -> F14[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], Out]: return _curry(f)
def curry15[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15], Out])                                                                                     -> F15[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], Out]: return _curry(f)
def curry16[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16], Out])                                                                         -> F16[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], Out]: return _curry(f)
def curry17[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17], Out])                                                             -> F17[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], Out]: return _curry(f)
def curry18[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18], Out])                                                 -> F18[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], Out]: return _curry(f)
def curry19[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19], Out])                                     -> F19[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], Out]: return _curry(f)
def curry20[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20], Out])                         -> F20[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], [In20], Out]: return _curry(f)
def curry21[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21], Out])             -> F21[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], [In20], [In21], Out]: return _curry(f)
def curry22[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21, In22, Out](f: F1[[In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21, In22], Out]) -> F22[[In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], [In20], [In21], [In22], Out]: return _curry(f)
# fmt: on


# fmt: off
def curry_method(f: Callable[Concatenate[Self, A, P], T]) -> Callable[[Self, A], Any]: return _curry_method(f)
def curry_method0[Self, Out](f: F1[[Self], Out])                                                                                                                                                                                                                                                        -> F1[[Self], Out]: return f
def curry_method1[Self, In1, Out](f: F1[[Self, In1], Out])                                                                                                                                                                                                                                              -> F1[[Self, In1], Out]: return _curry_method(f)
def curry_method2[Self, In1, In2, Out](f: F1[[Self, In1, In2], Out])                                                                                                                                                                                                                                    -> F2[[Self, In1], [In2], Out]: return _curry_method(f)
def curry_method3[Self, In1, In2, In3, Out](f: F1[[Self, In1, In2, In3], Out])                                                                                                                                                                                                                          -> F3[[Self, In1], [In2], [In3], Out]: return _curry_method(f)
def curry_method4[Self, In1, In2, In3, In4, Out](f: F1[[Self, In1, In2, In3, In4], Out])                                                                                                                                                                                                                -> F4[[Self, In1], [In2], [In3], [In4], Out]: return _curry_method(f)
def curry_method5[Self, In1, In2, In3, In4, In5, Out](f: F1[[Self, In1, In2, In3, In4, In5], Out])                                                                                                                                                                                                      -> F5[[Self, In1], [In2], [In3], [In4], [In5], Out]: return _curry_method(f)
def curry_method6[Self, In1, In2, In3, In4, In5, In6, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6], Out])                                                                                                                                                                                            -> F6[[Self, In1], [In2], [In3], [In4], [In5], [In6], Out]: return _curry_method(f)
def curry_method7[Self, In1, In2, In3, In4, In5, In6, In7, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7], Out])                                                                                                                                                                                  -> F7[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], Out]: return _curry_method(f)
def curry_method8[Self, In1, In2, In3, In4, In5, In6, In7, In8, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8], Out])                                                                                                                                                                        -> F8[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], Out]: return _curry_method(f)
def curry_method9[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9], Out])                                                                                                                                                              -> F9[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], Out]: return _curry_method(f)
def curry_method10[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10], Out])                                                                                                                                                 -> F10[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], Out]: return _curry_method(f)
def curry_method11[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11], Out])                                                                                                                                     -> F11[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], Out]: return _curry_method(f)
def curry_method12[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12], Out])                                                                                                                         -> F12[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], Out]: return _curry_method(f)
def curry_method13[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13], Out])                                                                                                             -> F13[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], Out]: return _curry_method(f)
def curry_method14[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14], Out])                                                                                                 -> F14[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], Out]: return _curry_method(f)
def curry_method15[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15], Out])                                                                                     -> F15[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], Out]: return _curry_method(f)
def curry_method16[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16], Out])                                                                         -> F16[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], Out]: return _curry_method(f)
def curry_method17[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17], Out])                                                             -> F17[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], Out]: return _curry_method(f)
def curry_method18[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18], Out])                                                 -> F18[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], Out]: return _curry_method(f)
def curry_method19[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19], Out])                                     -> F19[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], Out]: return _curry_method(f)
def curry_method20[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20], Out])                         -> F20[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], [In20], Out]: return _curry_method(f)
def curry_method21[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21], Out])             -> F21[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], [In20], [In21], Out]: return _curry_method(f)
def curry_method22[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21, In22, Out](f: F1[[Self, In1, In2, In3, In4, In5, In6, In7, In8, In9, In10, In11, In12, In13, In14, In15, In16, In17, In18, In19, In20, In21, In22], Out]) -> F22[[Self, In1], [In2], [In3], [In4], [In5], [In6], [In7], [In8], [In9], [In10], [In11], [In12], [In13], [In14], [In15], [In16], [In17], [In18], [In19], [In20], [In21], [In22], Out]: return _curry_method(f)
# fmt: on


def tupled(f: Callable[..., T]) -> Callable[[tuple], T]:
    def g(t: tuple) -> T:
        return f(*t)

    return g
