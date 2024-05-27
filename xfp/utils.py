from typing import Any

# Element type alias
type E = Any
type Unused = None


def id[E](e: E) -> E:
    return e
