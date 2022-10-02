from typing import Any, TypeVar

G = TypeVar("G")


def guard(value: G, message: str = "Assertion Error"):
    if not value:
        raise AssertionError(message)
    return value
