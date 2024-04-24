from xfp import Xeffect

option = Xeffect.from_optional(3).map(lambda x: x * 2).map(lambda x: str(x) * 3)

print("THIRD CONSUMPTION")
option.foreach(print)

print("FOURTH CONSUMPTION")
(
    option.flatMap(lambda x: Xeffect.from_optional(None if len(x) > 0 else x)).foreach(
        print
    )
)

(
    option.flatMap(lambda x: Xeffect.from_optional(None if len(x) == 0 else x)).foreach(
        print
    )
)

print("FIFTH CONSUMPTION")
out = option.flatMap(lambda x: Xeffect(Xeffect.key, None, "Error")).foreach(print)

out2 = Xeffect(Xeffect.key, None, "Error").flatMap(
    lambda x: Xeffect.from_optional(None if len(x) > 0 else x)
)  # .foreach(print)
out3 = Xeffect.from_optional(None).flatMap(
    lambda x: Xeffect.from_optional(None if len(x) > 0 else x)
)  # .foreach(print)
print(out.right_value)
print(out2.right_value)
print(out3.right_value)
