"""https://www.flaticon.com"""

from micropython import const

BRIGHTNESS_MANUAL_8x8 = const(
b'\x18\x7e\x7e\xe7\xe7\x7e\x7e\x18'
)

BRIGHTNESS_MANUAL_16x16 = const(
b'\x01\x80\x03\xc0\x3f\xfc\x3f\xfc\x3f\xfc\x3d\xbc\x7c\x3e\xfc\x3f'
b'\xfc\x3f\x7d\xbe\x3d\xbc\x3f\xfc\x3f\xfc\x3f\xfc\x03\xc0\x01\x80'
)

BRIGHTNESS_MANUAL_32x32 = const(
b'\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00'
b'\x07\xff\xff\xe0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0'
b'\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x1f\xf3\xcf\xf8'
b'\x3f\xf1\x8f\xfc\x7f\xf1\x8f\xfe\xff\xf0\x0f\xff\xff\xf0\x0f\xff'
b'\xff\xf2\x4f\xff\xff\xf3\xcf\xff\x7f\xf3\xcf\xfe\x3f\xf3\xcf\xfc'
b'\x1f\xf3\xcf\xf8\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0'
b'\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x07\xff\xff\xe0'
b'\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00'
)
