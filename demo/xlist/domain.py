from dataclasses import dataclass
from functools import total_ordering
from typing import Any


@total_ordering
@dataclass(frozen=True, eq=False)
class Sale:
    id: int
    ean: int
    ref_date: str
    amount: float

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Sale):
            return False
        else:
            return self.amount == other.amount

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Sale):
            raise TypeError(
                f"'<' not supported between instances of '{type(other)}' and 'Sale'"
            )
        else:
            return self.amount < other.amount
