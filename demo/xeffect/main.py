from typing import Callable
from .operation import load_csv
from xfp import Xeffect


# 'FP LANGUAGES' STYLE

print("@@@ FUNCTIONAL STYLE @@@")
print("@@@@@ HANDLING OWNED ERRORS @@@@@")


def buy_yummy(fruit: str) -> Callable:
    def inner(cart: list) -> Xeffect[Exception, list]:
        if fruit in ("apple", "peach", "blackberry"):
            new_cart = cart.copy()
            new_cart.append(fruit)
            return Xeffect.right(new_cart)
        else:
            return Xeffect.left(Exception(f"eurgh, {fruit} is not yummy"))

    return inner


(
    Xeffect.right(list())
    .flat_map(buy_yummy("apple"))
    .flat_map(buy_yummy("peach"))
    .foreach(lambda x: print(f"see my cart : {x}"))
)

(
    Xeffect.right(list())
    .flat_map(buy_yummy("apple"))
    .flat_map(buy_yummy("brusselsprouts"))
    .flat_map(buy_yummy("anchovies"))
    .flat_map(buy_yummy("peach"))
    .foreach_left(lambda x: print(f"see my not so yummy cart : {x}"))
)

print("@@@@@ HANDLING RAISED ERRORS @@@@@")

# TODO - pas sûr que ça marche, 'but_empty' lève pas d'erreur ...

safe_load: Xeffect[Exception, str] = Xeffect.from_unsafe(lambda: load_csv("file.csv"))
safe_load_but_empty: Xeffect[Exception, str] = Xeffect.from_unsafe(
    lambda: load_csv("file.csv")
)

safe_load.foreach(print)
safe_load_but_empty.foreach_left(print)


# PYTHONIC STYLE

print("@@@ PYTHONIC STYLE @@@")
print("@@@@@ HANDLING OWNED ERRORS @@@@@")


def buy_yummy_imp(cart: list, fruit: str) -> None:
    if fruit in ("apple", "peach", "blackberry"):
        cart.append(fruit)
    else:
        raise Exception(f"eurgh, {fruit} is not yummy")


cart = list()

try:
    buy_yummy_imp(cart, "apple")
    buy_yummy_imp(cart, "peach")
    print(f"see my cart : {cart}")
except Exception:
    pass

cart_fail = list()

try:
    buy_yummy_imp(cart_fail, "apple")
    buy_yummy_imp(cart_fail, "brusselsprouts")
    buy_yummy_imp(cart_fail, "anchovies")
    buy_yummy_imp(cart_fail, "peached")
except Exception as e:
    print(f"see my not so yummy cart : {e}")


print("@@@@@ HANDLING RAISED ERRORS @@@@@")

try:
    loaded: str = load_csv("file.csv")
    print(loaded)
    this_raises: str = load_csv("file.csv")
except Exception as e:
    print(e)
