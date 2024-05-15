from dataclasses import dataclass
from functools import total_ordering
from typing import Self


@total_ordering
@dataclass(frozen=True, eq=False)
class Sale:
    id: int
    ean: int
    ref_date: str
    amount: float

    def __eq__(self, other: Self) -> bool:
        return self.amount == other.amount

    def __lt__(self, other: Self) -> bool:
        return self.amount < other.amount
