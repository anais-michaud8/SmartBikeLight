"""https://www.flaticon.com"""

from micropython import const

BRAKE_8x8 = const(
b'\x00\x11\x37\xff\xff\x37\x11\x00'
)

BRAKE_16x16 = const(
b'\x00\x00\x00\x01\x03\x83\x07\x8f\x0f\x9f\x1f\xbf\x7f\xff\xff\xff'
b'\xff\xff\x7f\xff\x1f\xbf\x0f\x9f\x07\x8f\x03\x83\x00\x01\x00\x00'
)

BRAKE_32x32 = const(
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x80\x07'
b'\x00\x07\x80\x0f\x00\x0f\x80\x1f\x00\x1f\x80\x3f\x00\x3f\x80\xff'
b'\x00\xff\x81\xff\x01\xff\x83\xff\x03\xff\x87\xff\x07\xff\x9f\xff'
b'\x0f\xff\xbf\xff\x3f\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff'
b'\xff\xff\xff\xff\x7f\xff\xff\xff\x3f\xff\xff\xff\x0f\xff\xbf\xff'
b'\x07\xff\x9f\xff\x03\xff\x87\xff\x01\xff\x83\xff\x00\xff\x81\xff'
b'\x00\x3f\x80\xff\x00\x1f\x80\x3f\x00\x0f\x80\x1f\x00\x07\x80\x0f'
b'\x00\x01\x80\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
)
