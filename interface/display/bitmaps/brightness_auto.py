"""https://www.flaticon.com"""

from micropython import const

BRIGHTNESS_AUTO_8x8 = const(
b'\x18\x7e\x7e\xe7\xe7\x7e\x7e\x18'
)

BRIGHTNESS_AUTO_16x16 = const(
b'\x01\x80\x03\xc0\x3f\xfc\x3f\xfc\x3f\xfc\x3e\x7c\x7c\x3e\xfc\x3f'
b'\xfc\x3f\x7d\x3e\x3d\xbc\x3f\xfc\x3f\xfc\x3f\xfc\x03\xc0\x01\x80'
)

BRIGHTNESS_AUTO_32x32 = const(
b'\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00'
b'\x07\xff\xff\xe0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0'
b'\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x1f\xfc\x3f\xf8'
b'\x3f\xf8\x1f\xfc\x7f\xf9\x9f\xfe\xff\xf9\x9f\xff\xff\xf9\x9f\xff'
b'\xff\xf8\x1f\xff\xff\xf8\x1f\xff\x7f\xf9\x9f\xfe\x3f\xf9\x9f\xfc'
b'\x1f\xf9\x9f\xf8\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0'
b'\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x07\xff\xff\xe0'
b'\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00'
)
