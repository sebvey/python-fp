from typing import Protocol

# IMPOSE STRICT SIGNATURES WITH PROTOCOLS


class MyFuncType(Protocol):
    def __call__(self, a_positional: int, /, b_both: int) -> None: ...


def compliant_func(a_positional: int, /, b_both: int) -> None: ...


# names don't matter for positional arguments
def still_compliant_func(alpha_positional: int, /, b_both: int) -> None: ...


# 'handling' non compliant (keyword) instead of both
def non_compliant_handling_func(a_positional: int, *, b_both: int) -> None: ...


# keyword argument badly named
def non_compliant_arg_name_func(a_positional: int, /, b: int) -> None: ...


func_list: list[MyFuncType] = []
func_list.append(compliant_func)
func_list.append(still_compliant_func)

func_list.append(non_compliant_handling_func)  # type: ignore
func_list.append(non_compliant_arg_name_func)  # type: ignore

# /!\ Not always easy to understand typing errors
# (pyright is provides better explanations than mypy)
# /!\ (as yet) We can't mix new keyword args with ParamSpec, we would have to deal with overlapping)
