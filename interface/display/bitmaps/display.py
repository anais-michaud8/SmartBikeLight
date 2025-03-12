"""https://www.flaticon.com"""

from micropython import const

DISPLAY_8x8 = const(
b'\x7e\x81\x99\xbd\x99\x81\x7e\x3c'
)

DISPLAY_16x16 = const(
b'\x3f\xfc\x7f\xfe\xc0\x03\xc1\x83\x81\xc1\x87\xe1\x86\x61\x86\x61'
b'\x87\xe1\x81\x81\xc0\x03\x60\x06\x3f\xfc\x00\x00\x07\xe0\x07\xe0'
)

DISPLAY_32x32 = const(
b'\x00\x00\x00\x00\x0f\xff\xff\xf0\x1f\xff\xff\xf8\x3f\xff\xff\xfc'
b'\x78\x00\x00\x1e\xf0\x00\x00\x0f\xe0\x01\x80\x07\xe0\x01\x80\x07'
b'\xe0\x03\xc0\x07\xe0\x37\xfc\x07\xe0\x7f\xfe\x07\xe0\x3e\x3c\x07'
b'\xe0\x1c\x38\x07\xe0\x18\x1c\x07\xe0\x1c\x18\x07\xe0\x3c\x3c\x07'
b'\xe0\x7f\xfe\x07\xe0\x3f\xfe\x07\xe0\x03\xe0\x07\xe0\x01\xc0\x07'
b'\xe0\x01\x80\x07\xf0\x00\x00\x0f\x78\x00\x00\x1e\x3f\xff\xff\xfc'
b'\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x00\x00\x00\x00\x00\x00\x00\x00'
b'\x00\x3f\xfc\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x00\x00\x00'
)
