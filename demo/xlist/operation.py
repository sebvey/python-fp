from .domain import Sale
from dataclasses import replace


def convert_amount(s: Sale) -> Sale:
    return replace(s, amount=s.amount * 1.1)


def is_day_of_month(day_of_month: int):
    def predicate(sale: Sale):
        expected_DOM = str(day_of_month).rjust(2, "0")
        actual_DOM = sale.ref_date[-2:]

        return True if actual_DOM == expected_DOM else False

    return predicate
