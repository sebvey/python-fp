from xfp import Xlist
from .domain import Sale
from . import operation as op

from operator import attrgetter


sales = [
    Sale(id=1, ean=1, ref_date="2024-04-01", amount=10),
    Sale(id=2, ean=2, ref_date="2024-04-01", amount=20),
    Sale(id=3, ean=2, ref_date="2024-04-02", amount=20),
    Sale(id=4, ean=3, ref_date="2024-05-01", amount=40),
    Sale(id=5, ean=4, ref_date="2024-05-01", amount=5),
]

zsales = Xlist(sales)


# 'FP LANGUAGES' STYLE
print("@@@ FUNCTIONAL STYLE @@@")

(
    zsales.map(op.convert_amount)
    .filter(op.is_day_of_month(1))
    .sorted(key=attrgetter("amount"))
    .foreach(print)
)


print("@@@ zsales immutable, and iterable")

# PYTHONIC STYLE
print("@@@ PYTHONIC STYLE @@@")

sales = map(op.convert_amount, sales)
sales = list(filter(op.is_day_of_month(1), sales))
sales.sort(key=attrgetter("amount"))

for s in sales:
    print(s)
