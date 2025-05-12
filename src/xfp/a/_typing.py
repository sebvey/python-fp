from collections.abc import Awaitable, Callable

from xfp import Xresult


type AwaitableXR[L, R] = Awaitable[Xresult[L, R]]

type CoFunc[**P, X] = Callable[P, Awaitable[X]]
type CoFunc1[A, X] = CoFunc[[A], X]

type CoFuncXR[**P, L, R] = Callable[P, AwaitableXR[L, R]]
type CoFunc1XR[A, L, R] = CoFuncXR[[A], L, R]
