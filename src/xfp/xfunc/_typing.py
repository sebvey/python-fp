from __future__ import annotations
from typing import Any, Coroutine

from xfp import Xresult

type PyCoXR[L, R] = Coroutine[Any, Any, Xresult[L, R]]
type PyCo[X] = Coroutine[Any, Any, X]
