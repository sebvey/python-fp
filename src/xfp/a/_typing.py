from collections.abc import Awaitable, Callable

from xfp import Xresult

# conventions
# L,R -> Left and Right of a Xresult
# R -> result (or right only)
# when composing, the same with suffix 'o' (other)

type AwaitableXR[L, R] = Awaitable[Xresult[L, R]]

type CoFunc[**P, R] = Callable[P, Awaitable[R]]
type CoFunc1[A, R] = CoFunc[[A], R]

type CoFuncXR[**P, L, R] = Callable[P, AwaitableXR[L, R]]
type CoFunc1XR[A, L, R] = CoFuncXR[[A], L, R]
