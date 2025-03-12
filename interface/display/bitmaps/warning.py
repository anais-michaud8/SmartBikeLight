"""https://www.flaticon.com"""

from micropython import const

WARNING_8x8 = const(
b'\x00\x18\x3c\x24\x7e\xe7\xff\x7e'
)

WARNING_16x16 = const(
b'\x00\x00\x01\x80\x03\xc0\x07\xe0\x06\x60\x0e\x70\x1e\x78\x1e\x78'
b'\x3e\x7c\x3f\xfc\x7f\xfe\xfe\x7f\xfe\x7f\xff\xff\x7f\xfe\x00\x00'
)

WARNING_32x32 = const(
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x00\x00\x0f\xf0\x00'
b'\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00\x3f\xfc\x00'
b'\x00\x7c\x3e\x00\x00\x7c\x3e\x00\x00\xfc\x3f\x00\x00\xfc\x3f\x00'
b'\x01\xfc\x3f\x80\x03\xfc\x3f\xc0\x03\xfc\x3f\xc0\x07\xfc\x3f\xe0'
b'\x07\xfc\x3f\xe0\x0f\xfc\x3f\xf0\x1f\xfe\x7f\xf8\x1f\xff\xff\xf8'
b'\x3f\xff\xff\xfc\x3f\xfc\x3f\xfc\x7f\xf8\x1f\xfe\xff\xf8\x1f\xff'
b'\xff\xf8\x1f\xff\xff\xfc\x3f\xff\xff\xff\xff\xff\xff\xff\xff\xff'
b'\x7f\xff\xff\xfe\x3f\xff\xff\xfc\x00\x00\x00\x00\x00\x00\x00\x00'
)
