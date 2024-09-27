# XITER EXPERIMENTATIONS ##############

from xfp import Xiter

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Sale:
    ean: int
    ref_date: str
    amount: float


def double(s: Sale) -> Sale:
    return replace(s, amount=s.amount * 2)


def add_one(s: Sale) -> Sale:
    return replace(s, amount=s.amount + 1)


def is_day_of_month(day_of_month: int):
    def predicate(sale: Sale):
        expected_DOM = str(day_of_month).rjust(2, "0")
        actual_DOM = sale.ref_date[-2:]

        match actual_DOM:
            case d if d == expected_DOM:
                return True
            case _:
                return False

    return predicate


# xiterize only 'immutable' data
# xiter is based on iterators
# lazy transfo, we collect when consuming the iterator
# so if data changed between transfos declaration and consuption ...
# -> DEVELOPPER RESPONSABILITY TO RELY ON tuples, frozen dataclasses ...

sales = Xiter(
    [
        Sale(ean=1, ref_date="2024-04-01", amount=10),
        Sale(ean=2, ref_date="2024-04-01", amount=20),
        Sale(ean=2, ref_date="2024-04-02", amount=20),
    ]
)

new_sales = (
    sales.filter(is_day_of_month(1)).map(double).map(add_one)
    #        .flatMap(lambda x: [x, x])
)

print("FIRST CONSUMPTION")
new_sales.foreach(print)

print("SECOND CONSUMPTION")
new_sales.foreach(print)
