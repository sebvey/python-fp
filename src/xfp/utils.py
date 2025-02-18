from typing import Any, Protocol
import xfp.functions as f
from deprecation import deprecated  # type: ignore

# type: ignore
deprecated("1.1.0", "2.0.0", details="moved to xfp.functions")
id: f.F1[[Any], Any] = f.id
deprecated("1.1.0", "2.0.0", details="moved to xfp.functions")
tupled: f.F2[[f.F1[..., Any]], [tuple], Any] = f.tupled
deprecated("1.1.0", "2.0.0", details="moved to xfp.functions")
curry: f.F2[[f.F1[..., Any]], ..., Any] = f.curry
deprecated("1.1.0", "2.0.0", details="moved to xfp.functions")
curry_method: f.F2[[f.F1[..., Any]], ..., Any] = f.curry_method


# internally used for type checking
class _SupportsDunderLT(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


class _SupportsDunderGT(Protocol):
    def __gt__(self, other: Any, /) -> bool: ...


type _Comparable = _SupportsDunderGT | _SupportsDunderLT
