import os
from typing import overload


@overload
def get_env(variable: str, expected_type: type[bool]) -> bool | None: ...


@overload
def get_env(variable: str, expected_type: type[int]) -> int | None: ...


@overload
def get_env(variable: str, expected_type: type[str]) -> str | None: ...


def get_env(
    variable: str, expected_type: type[bool | int | str]
) -> bool | int | str | None:
    val = os.getenv(variable)

    if val is None:
        val = None
    elif expected_type is bool:
        if val.lower() in ("true", "1"):
            val = True
        elif val.lower() in ("false", "0"):
            val = False
        else:
            val = None
    elif expected_type is int:
        try:
            val = int(val)
        except ValueError:
            val = None
    elif expected_type is str:
        pass
    else:
        raise TypeError(f"Unsupported type: {expected_type}")

    return val
