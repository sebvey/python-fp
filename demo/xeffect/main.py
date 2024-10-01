from .operation import load_csv
from xfp import Xresult, curry, Xtry


# 'FP LANGUAGES' STYLE

print("@@@ FUNCTIONAL STYLE @@@")
print("@@@@@ HANDLING OWNED ERRORS @@@@@")


@curry
def buy_yummy(fruit: str, cart: list) -> Xresult[Exception, list]:
    if fruit in ("apple", "peach", "blackberry"):
        new_cart = cart.copy()
        new_cart.append(fruit)
        return Xtry.Success(new_cart)
    else:
        return Xtry.Failure(Exception(f"eurgh, {fruit} is not yummy"))


(
    Xtry.Success(list())
    .flat_map(buy_yummy("apple"))
    .flat_map(buy_yummy("peach"))
    .foreach(lambda x: print(f"see my cart : {x}"))
)

(
    Xtry.Success(list())
    .flat_map(buy_yummy("apple"))
    .flat_map(buy_yummy("brusselsprouts"))
    .flat_map(buy_yummy("anchovies"))
    .flat_map(buy_yummy("peach"))
    .foreach_left(lambda x: print(f"see my not so yummy cart : {x}"))
)

print("@@@@@ HANDLING RAISED ERRORS @@@@@")

safe_load: Xresult[Exception, str] = Xtry.from_unsafe(lambda: load_csv("file.csv"))
safe_load_but_empty: Xresult[Exception, str] = Xtry.from_unsafe(
    lambda: load_csv("file.cv")
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
