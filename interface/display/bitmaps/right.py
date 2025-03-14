"""https://www.flaticon.com"""

from micropython import const

RIGHT_8x8 = const(
b'\x20\x30\x38\x3c\x38\x38\x30\x20'
)

RIGHT_16x16 = const(
b'\x0c\x00\x0e\x00\x0e\x00\x0f\x00\x0f\x80\x0f\xc0\x0f\xe0\x0f\xe0'
b'\x0f\xe0\x0f\xc0\x0f\xc0\x0f\x80\x0f\x00\x0e\x00\x0c\x00\x0c\x00'
)

RIGHT_32x32 = const(
b'\x00\x60\x00\x00\x00\xf0\x00\x00\x00\xf8\x00\x00\x00\xfc\x00\x00'
b'\x00\xfc\x00\x00\x00\xfe\x00\x00\x00\xff\x00\x00\x00\xff\x80\x00'
b'\x00\xff\xc0\x00\x00\xff\xc0\x00\x00\xff\xe0\x00\x00\xff\xf0\x00'
b'\x00\xff\xf8\x00\x00\xff\xfc\x00\x00\xff\xfc\x00\x00\xff\xfe\x00'
b'\x00\xff\xfe\x00\x00\xff\xfc\x00\x00\xff\xf8\x00\x00\xff\xf0\x00'
b'\x00\xff\xf0\x00\x00\xff\xe0\x00\x00\xff\xc0\x00\x00\xff\x80\x00'
b'\x00\xff\x00\x00\x00\xff\x00\x00\x00\xfe\x00\x00\x00\xfc\x00\x00'
b'\x00\xf8\x00\x00\x00\xf0\x00\x00\x00\x70\x00\x00\x00\x60\x00\x00'
)
