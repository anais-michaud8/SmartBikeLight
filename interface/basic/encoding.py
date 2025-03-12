
import gc
gc.collect()

import struct


class Encoder:
    def __init__(self, fmt: str, pre=None, post=None) -> None:
        self.fmt = fmt
        self.pre = pre
        self.post = post

    @property
    def size(self) -> int:
        return struct.calcsize(self.fmt)

    def encode(self, value) -> bytes:
        return struct.pack(self.fmt, value if self.pre is None else self.pre(value) if value is not None else b'0')

    def decode(self, value: bytes):
        try:
            decoded = struct.unpack(self.fmt, value)[0]
        except ValueError:
            return None
        if self.post is not None:
            return self.post(decoded)
        return decoded

    def from_str(self, value: str):
        if self.fmt == "?":
            return value.lower() == "true"
        elif self.fmt.lower() == "b":
            return int(value)
        return value


gc.collect()


class ArrayEncoder:
    def __init__(self, *encoders: Encoder) -> None:
        self.encoders: tuple[Encoder, ...] = encoders

    @property
    def size(self) -> int:
        return sum([encoder.size for encoder in self.encoders])

    def encode(self, value: list | tuple) -> bytes:
        return b''.join([e.encode(value[i]) if i < len(value) else b'\x00'*e.size for i, e in enumerate(self.encoders)])

    def decode(self, value: bytes) -> list:
        res = []
        index = 0
        for encoder in self.encoders:
            res.append(encoder.decode(value[index:index+encoder.size]))
            index += encoder.size
            if index+encoder.size > len(value):
                break
        return res

    def from_str(self, value: str):
        return [self.encoders[i].from_str(val) for i, val in enumerate(value.split(",")) if i < len(self.encoders)]


gc.collect()

BOOLEAN_ENCODER = Encoder("B", pre=lambda x: int(bool(x)), post=lambda x: bool(int(x)))
INT8_ENCODER = Encoder("b", pre=int, post=int)
UINT8_ENCODER = Encoder("B", pre=int, post=int)
UINT16_ENCODER = Encoder("H", pre=int, post=int)
PERCENTAGE_INT_ENCODER = Encoder("B", pre=int, post=int)
PERCENTAGE_FLOAT_ENCODER = Encoder("b", pre=lambda x: round(float(x)*100), post=lambda x: float(x)/100)
FLOAT_ENCODER = Encoder("f", pre=float, post=float)
SMALL_FLOAT_ENCODER = Encoder("e", pre=float, post=float)

Boolean = bool
Int8 = int
Uint8 = int
PercentageInt = int
PercentageFloat = float
Duration = float
Float = float
Colour = int
Uint16 = int


gc.collect()
