
import gc
gc.collect()

import asyncio

""" List """


def to_list(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, tuple):
        return list(data)
    if data is None:
        return []
    return [data]


""" Formatters """

def rounder(value: float, rounding: int) -> float | int:
    return round(value, rounding) if rounding > 0 else int(value)


def adjuster(value: float | str | bool, padding: int = 1, rounding: int = 0,
             left: bool = False, right: bool = True, character: str = " ") -> str:
    rounded = rounder(value, rounding) if isinstance(value, float) else value
    pad = (padding-len(str(rounded))) * character
    val = str(rounded)[:padding]
    return pad + val if right else val + pad if left else pad[0:len(pad)//2] + val + pad[len(pad)//2:-1]


def formatting(value: float | str | bool, rounding: int = 0, converter=None, formatter: str = "{}"):
    if converter is not None and value is not None:
        value = converter(value)
    if value is None:
        value = ""
    if not isinstance(value, str):
        value = rounder(value, rounding)
    return formatter.format(value)


def string(
        value: float | str | bool,
        padding: int | None = 1, rounding: int = 0, left: bool = False, right: bool = True, character: str = " ",
        converter=None, formatter: str = "{}"
    ):
    if converter is not None and value is not None:
        value = converter(value)
    if value is None:
        value = ""
    extra = len(formatter.replace("{}", ""))
    if padding is not None:
        return formatter.format(adjuster(value, padding-extra, rounding, left, right, character))
    return formatter.format(value)


def time_formatter(value: float, unit: str = "h") -> str:
    hours = int(value)
    mins = int((value - hours)*60)
    text = f"{hours:02}{unit}{mins:02}"
    return text


""" Memory """

async def clean(wait: int | float = 3):
    while True:
        await asyncio.sleep(wait)
        gc.collect()


async def memory(wait: int | float = 3, printer=print, **kwargs):
    while True:
        await asyncio.sleep(wait)
        gc.collect()
        printer(f"Memory: {gc.mem_free()}", **kwargs)


gc.collect()

