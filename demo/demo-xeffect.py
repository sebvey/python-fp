from xfp import *

"""
taList = list()
taMappedList = map(taList, lambda x: x*x)
taFilteredList = filter(taMappedList, lambda x: x % 2 == 0)



taList
  .map(lambda x: x*x)
  .filter(lambda x: x % 2 == 0)
"""

(
    Xlist([1, 2, 3, 4])
      .flat_map(lambda x: [x, x]) # Xlist([1, 1, 2, 2, 3, 3, 4, 4])      
)

def div(x: float, y: float) -> Xeffect[float, str]:
    if y == 0:
        return Xeffect(XFXBranch.RIGHT, "banane")
    return Xeffect(XFXBranch.LEFT, x / y)

Xeffect.from_unsafe(lambda: div(3, 0))

(
  div(3, 1)
    .flat_map(lambda x:float: div(1, x))
    .fold(0)(lambda x: x - 3)
)