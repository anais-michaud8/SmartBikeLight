
import gc
gc.collect()

from interface.display import bitmaps
from interface.display import fonts

from interface.basic.utils import formatting


WIDTH = 135
HEIGHT = 240

Colour = int

gc.collect()


# =========================== #
#            Styles           #
# =========================== #


class Colours:
    BLACK = 0x0000
    BLUE = 0x43b7 # 0x001F
    RED = 0xF800
    GREEN = 0x07E0
    CYAN = 0x07FF
    MAGENTA = 0xF81F
    YELLOW = 0xFFE0
    ORANGE = 0xFBE0
    WHITE = 0xFFFF


gc.collect()


class Font:

    def __init__(self, width: int, height: int, font: memoryview):
        self.WIDTH: int = width
        self.HEIGHT: int = height
        self.FIRST: int = 0x00
        self.LAST: int = 0xff
        self.FONT: memoryview = font

    @classmethod
    def from_module(cls, module):
        return cls(module.WIDTH, module.HEIGHT, module.FONT)

    @classmethod
    def from_size(cls, height: int = 16, bold: bool = False, large: bool = True):
        if height == 32:
            return cls.from_module(fonts.vga16x32) if not bold else cls.from_module(fonts.vga16x32_bold)
        if height == 16:
            if bold:
                return cls.from_module(fonts.vga16x16_bold)
            if not large:
                return cls.from_module(fonts.vga8x16)
            return cls.from_module(fonts.vga16x16)
        return cls.from_module(fonts.vga8x8)

    @classmethod
    def get_size(cls, height: int = 16, bold: bool = False, large: bool = True):
        if height == 32:
            return 16, 32
        if height == 16:
            if bold:
                return 16, 16
            if not large:
                return 8, 16
            return 16, 16
        return 8, 8



gc.collect()


class Bitmap:

    def __init__(self, width: int, height: int, bitmap: memoryview, colour: Colour = Colours.WHITE, background: Colour = Colours.BLACK):
        self.WIDTH: int = width
        self.HEIGHT: int = height
        self.BITS: int = width * height
        self.BPP: int = 1
        self.BITMAP: memoryview = bitmap
        self.COLORS: int = 2
        self.PALETTE: list[Colour] = [background, colour]

    @classmethod
    def from_size(cls, name: str, size: int = 16, colour: Colour = Colours.WHITE, background: Colour = Colours.BLACK):
        size = 8 if size != 32 and size != 16 else size

        name = name.replace("-", "_").replace(" ", "_").lower()

        # Get icon
        name = f"{name.upper()}_{size}x{size}"
        for icon, value in bitmaps.__dict__.items():
            if icon == name:
                return cls(size, size, memoryview(value), colour=colour, background=background)
        return None


gc.collect()


# =========================== #
#           Display           #
# =========================== #


class Display:

    def __init__(self, display,
                 width: int = WIDTH, height: int = HEIGHT, landscape: bool = False, background: int = Colours.BLACK,
                 activation: bool = True, brightness: int = 100):
        self.display = display
        self.landscape = landscape
        self.width, self.height = (height, width) if landscape else (width, height)
        self.background = background
        self.fill()
        self.activation = activation
        self.set_activation(activation)
        self.set_brightness(brightness)

    @classmethod
    def make(cls, _class, width: int = WIDTH, height: int = HEIGHT, landscape: bool = False, background: int = Colours.BLACK,
                 activation: bool = True, brightness: int = 100, **kwargs) -> "Display":
        return cls(
            _class(
                width=width, height=height, landscape=landscape, background=background,
                activation=activation, brightness=brightness, **kwargs
            ),
            width=width, height=height, landscape=landscape, background=background,
            activation=activation, brightness=brightness
        )

    # Activation

    def set_activation(self, value: bool):
        self.activation = value
        self.display.sleep_mode(not self.activation)

    def toggle(self, _=None):
        self.set_activation(not self.activation)

    def turn_off(self, _=None):
        self.set_activation(False)

    def turn_on(self, _=None):
        self.set_activation(True)

    def set_brightness(self, value: int):
        self.display.set_brightness(value)

    # Helpers

    def _get_colours(self, colour: Colour, background: Colour | None = None, inverse: bool = False) -> tuple[Colour, Colour]:
        background = background if background is not None else self.background
        return (colour, background) if not inverse else (background, colour)

    def anchor(self, x: int, y: int, w: int, h: int,
               wf: int | None = None, hf: int | None = None,
               anchor: int = 5, full: bool = False) -> tuple[int, int]:
        # Get full width and full height
        wf = self.width if wf is None and full else w if wf is None else wf
        hf = self.height if hf is None and full else h if hf is None else hf
        # Get y coordinate
        y = y if anchor in [1, 2, 3] else y + (hf - h)//2 if anchor in [4, 5, 6] else y + hf-h
        # Get x coordinate
        x = x if anchor in [1, 4, 7] else x + (wf - w)//2 if anchor in [2, 5, 8] else x + wf-w
        return x, y

    def restrain(self, x: int, y: int, w: int, h: int,):
        x = min([max([0, x]), self.width-1])
        y = min([max([0, y]), self.height-1])

        w = min([max([0, w]), self.width-x-1])
        h = min([max([0, h]), self.height-y-1])
        return x, y, w, h

    """ Shapes """

    def fill(self, w: int | None = None, h: int | None = None,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE,
             anchor: int | None = 5, wf: int | None = None, hf: int | None = None, full: bool = False):

        # Get background from display and inverse colours if needed
        colour, _ = self._get_colours(colour=self.background, background=colour, inverse=inverse)

        # Get size
        w = w if w is not None else self.width - x
        h = h if h is not None else self.height - y

        # Anchor
        if anchor is not None:
            x, y = self.anchor(x, y, w, h, wf, hf, full=full, anchor=anchor)

        # Fill
        self.display.fill_rect(x, y, w, h, colour)

    def outline(self, w: int | None = None, h: int | None = None, fill: bool = False, thickness: int = 1,
                x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                anchor: int | None = 5, wf: int | None = None, hf: int | None = None, full: bool = False):

        # Get background from display and inverse colours if needed
        colour, b = self._get_colours(colour, background=self.background if background is None else background, inverse=inverse)

        # Get size
        w = w if w is not None else self.width - x
        h = h if h is not None else self.height - y

        # Anchor
        if anchor is not None:
            x, y = self.anchor(x, y, w, h, wf, hf, full=full, anchor=anchor)

        # Draw outline
        for i in range(thickness):
            self.display.rect(x + i, y + i, w - i * 2, h - i * 2, colour)

        # Fill
        if background is None and fill:
            background = b
        if background is not None:
            self.fill(x=x+thickness, y=y+thickness, w=w - thickness * 2, h=h - thickness * 2, colour=background)

    def line(self, length: int | None = None, thickness: int = 1, vertical: bool = False,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE,
             anchor: int | None = 5, wf: int | None = None, hf: int | None = None, full: bool = False):
        # Get background from display and inverse colours if needed
        colour, _ = self._get_colours(colour, background=self.background, inverse=inverse)

        # Get length
        length = length if length is not None else self.height - y if vertical else self.width - x

        # Anchor
        width, height = (thickness, length) if vertical else (length, thickness)
        x, y = self.anchor(x, y, width, height, wf, hf, full=full, anchor=anchor)

        # Draw line
        if vertical:
            if width == 1:
                self.display.vline(x, y, length, colour)
            else:
                self.display.fill_rect(x, y, thickness, length, colour)
        else:
            if height == 1:
                self.display.hline(x, y, length, colour)
            else:
                self.display.fill_rect(x, y, length, thickness, colour)

    """ Content """

    def text(self, text: str | int | float | bool,
             size: int = 8, large: bool = True, bold: bool = False, underline: bool = False,
             length: int | None = None, rounding: int = 0, converter=None, formatter: str = "{}",
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
             anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
             left: int = 0, right: int = 0):
        if text is None:
            return x-left, x

        # Get background from display and inverse colours if needed
        colour, background = self._get_colours(colour, background=background, inverse=inverse)

        # Get font
        font = Font.from_size(size, bold, large)
        w, h = Font.get_size(size, bold, large)

        # Anchor
        text = formatting(text, rounding=rounding, converter=converter, formatter=formatter)
        wf = length * w if wf is None and length is not None else wf
        hf = hf if hf is None else h + 1 if underline else h
        width = w * len(text) + left + right
        x, y = self.anchor(x+left, y, width, h, wf, hf, full=full, anchor=anchor)
        # Show text
        self.display.text(font, text, x, y, colour, background)

        # Underline (text + left + right)
        if underline:
            self.line(x=x-left, y=y + h, length=wf, vertical=False, colour=background)
            self.line(x=x-left, y=y + h, length=width, vertical=False, colour=colour)

        return x-left, x+w*len(text)

    def icon(self, icon: str, size: int = 8,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
             anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False):
        if icon is None:
            return
        # Get background from display and inverse colours if needed
        colour, background = self._get_colours(colour, background=background, inverse=inverse)

        # Get bitmap
        bitmap = Bitmap.from_size(icon, size, colour, background)

        # Anchor
        x, y = self.anchor(x, y, size, size, wf, hf, full=full, anchor=anchor)

        # Show bitmap
        if bitmap is not None:
            self.display.pbitmap(bitmap, x, y)


gc.collect()
