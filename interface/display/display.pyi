
from typing import Protocol

WIDTH = 135
HEIGHT = 240

# RGB888 Colour
Colour = int


class Font:
    WIDTH: int
    HEIGHT: int
    FIRST: int
    LAST: int
    FONT: memoryview

    def __init__(self, width: int, height: int, font: memoryview):
        ...

    @classmethod
    def from_module(cls, module) -> Font:
        ...

    @classmethod
    def from_size(cls, height: int = 16, bold: bool = False, large: bool = True):
        """

        Args:
            height ():
                The height of the font, 32, 16 or 8.
            bold ():
                Whether the font should be bold or not. Doesn't work for height 8 or not large.
            large ():
                Whether the font should be large or not for font size 16.

        Returns:
            The font
        """
        ...

    @classmethod
    def get_size(cls, height: int = 16, bold: bool = False, large: bool = True):
        """

        Args:
            height ():
                The height of the font, 32, 16 or 8.
            bold ():
                Whether the font should be bold or not. Doesn't work for height 8 or not large.
            large ():
                Whether the font should be large or not for font size 16.

        Returns:
            The width and height of the font
        """
        ...


class Bitmap:
    WIDTH: int
    HEIGHT: int
    BITS: int
    BPP: int
    COLORS: int
    PALETTE: list[Colour]
    BITMAP: memoryview

    def __init__(self, width: int, height: int, bitmap: memoryview, colour: Colour = Colours.WHITE, background: Colour = Colours.BLACK):
        ...

    @classmethod
    def from_size(cls, name: str, size: int = 16, colour: Colour = Colours.WHITE, background: Colour = Colours.BLACK) -> Bitmap:
        ...


class Colours:
    BLACK = 0x0000
    BLUE = 0x43b7 #0x001F
    RED = 0xF800
    GREEN = 0x07E0
    CYAN = 0x07FF
    MAGENTA = 0xF81F
    YELLOW = 0xFFE0
    ORANGE = 0xFBE0
    WHITE = 0xFFFF


class OLED(Protocol):
    width: int
    height: int
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, landscape: bool = False,
                 activation: bool = True, brightness: int = 100, **kwargs):
        ...

    def blit_buffer(self, buffer: bytearray, x: int, y: int, width: int, height: int):
        ...

    def sleep_mode(self, value: bool):
        ...

    def set_brightness(self, value: int):
        ...

    def vline(self, x: int, y: int, length: int, color: Colour):
        """Draw a vertical line. """
        ...

    def hline(self, x: int, y: int, length: int, color: Colour):
        """Draw a horizontal line. """
        ...

    def pixel(self, x: int, y: int, color: Colour):
        """ Draw a pixel. """
        ...

    def rect(self, x: int, y: int, w: int, h: int, color: Colour):
        """ Draw a rectangle of thickness 1. """
        ...

    def fill_rect(self, x: int, y: int, width: int, height: int, color: Colour):
        """ Draw a filled a rectangle. """
        ...

    def fill(self, color: Colour):
        """ Fill display. """
        ...

    def line(self, x0: int, y0: int, x1: int, y1: int, color: Colour):
        """Draw a line from (x0, y0) to (x1, y1)."""
        ...

    def text(self, font: Font, text: str, x0: int, y0: int, color: Colour = Colours.WHITE, background: Colour = Colours.BLACK):
        ...

    def pbitmap(self, bitmap: Bitmap, x: int, y: int):
        ...


# =========================== #
#           Display           #
# =========================== #


class Display:
    display: OLED
    landscape: bool
    width: int
    height: int
    background: Colour
    activation: bool

    def __init__(self, display: OLED,
                 width: int = WIDTH, height: int = HEIGHT, landscape: bool = False, background: int = Colours.BLACK,
                 activation: bool = True, brightness: int = 100):
        ...

    @classmethod
    def make(cls, _class: type[OLED], width: int = WIDTH, height: int = HEIGHT, landscape: bool = False, background: int = Colours.BLACK,
             activation: bool = True, brightness: int = 100, **kwargs) -> "Display":
        ...

    def set_brightness(self, value: int):
        ...

    def set_activation(self, value: bool):
        ...

    def toggle(self, _=None):
        ...

    def turn_off(self, _=None):
        ...

    def turn_on(self, _=None):
        ...

    def _get_colours(self, colour: Colour, background: Colour | None = None, inverse: bool = False) -> tuple[Colour, Colour]:
        ...

    def anchor(self, x: int, y: int, w: int, h: int,
               wf: int | None = None, hf: int | None = None,
               anchor: int = 5, full: bool = False) -> tuple[int, int]:
        ...

    def restrain(self, x: int, y: int, w: int, h: int, ):
        ...

    """ Shapes """

    def fill(self, w: int | None = None, h: int | None = None,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE,
             anchor: int | None = 5, wf: int | None = None, hf: int | None = None, full: bool = False):
        """
        Fill the display or a specific region.

        Args:
            w (): The width if specified otherwise use the display
            h (): The height if specified otherwise use the display

            x (): The x coordinate on which to start
            y (): The y coordinate on which to start
            inverse (): If inverse colour and background will be swapped
            colour (): The colour of the text

            anchor (): **To anchor:** The anchor (3x3 matrix)
            wf (): **To anchor:** The width if specified otherwise use the display's width if display otherwise the size
            hf (): **To anchor:** The height if specified otherwise use the display's height if display otherwise the size
            full (): **To anchor:** Whether to use the display dimension if no width and height specified otherwise use size

        Returns:

        """
        ...

    def outline(self, w: int | None = None, h: int | None = None, fill: bool = False, thickness: int = 1,
                x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                anchor: int | None = 5, wf: int | None = None, hf: int | None = None, full: bool = False):
        """
        Draw the outline of a region and optionally fill it.

        Args:
            w (): The width if specified otherwise use the display
            h (): The height if specified otherwise use the display
            fill (): Whether to fill if no background provided
            thickness (): The thickness of the outline

            x (): The x coordinate on which to start
            y (): The y coordinate on which to start
            inverse (): If inverse colour and background will be swapped
            colour (): The colour of the text
            background (): The colour of the background otherwise will be display's background

            anchor (): **To anchor:** The anchor (3x3 matrix)
            wf (): **To anchor:** The width if specified otherwise use the display's width if display otherwise the size
            hf (): **To anchor:** The height if specified otherwise use the display's height if display otherwise the size
            full (): **To anchor:** Whether to use the display dimension if no width and height specified otherwise use size

        Returns:

        """
        ...

    def line(self, length: int | None = None, thickness: int = 1, vertical: bool = False,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE,
             anchor: int | None = 5, wf: int | None = None, hf: int | None = None, full: bool = False):
        """
        Draw a vertical or horizontal line.

        Args:
            length (): The length of the line, if not provided use width or height of display
            thickness (): The thickness of the line
            vertical (): Whether the line is vertical

            x (): The x coordinate on which to start
            y (): The y coordinate on which to start
            inverse (): If inverse colour and background will be swapped
            colour (): The colour of the text

            anchor (): **To anchor:** The anchor (3x3 matrix)
            wf (): **To anchor:** The width if specified otherwise use the display's width if display otherwise the size
            hf (): **To anchor:** The height if specified otherwise use the display's height if display otherwise the size
            full (): **To anchor:** Whether to use the display dimension if no width and height specified otherwise use size

        Returns:

        """
        ...

    """ Content """

    def text(self, text: str | int | float | bool, size: int = 8,
             large: bool = True, bold: bool = False, underline: bool = False,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
             anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
             length: int | None = None, rounding: int = 0, converter=None, formatter: str = "{}",
             left: int = 0, right: int = 0) -> tuple[int, int]:
        """
        Draw text of given size.

        Args:
            text (): The value or text to display
            size (): The font size
            large (): Whether the font is large (for 16 when not large width is 8)
            bold (): Whether the font is bold (for 16 and 32 only)
            underline ():

            x (): The x coordinate on which to start
            y (): The y coordinate on which to start
            inverse (): If inverse colour and background will be swapped
            colour (): The colour of the text
            background (): The colour of the background otherwise will be display's background

            anchor (): **To anchor:** The anchor (3x3 matrix)
            wf (): **To anchor:** The width if specified otherwise use the display's width if display otherwise the size
            hf (): **To anchor:** The height if specified otherwise use the display's height if display otherwise the size
            full (): **To anchor:** Whether to use the display dimension if no width and height specified otherwise use size

            length (): To anchor: The maximum number of characters, will allow anchoring
            rounding (): The number of places to which to round
            converter (): The optional function to pass the value before formatting
            formatter (): The '{}' formatter to pass the converted value after rounding

            left (): Width of another widget on the left to anchor properly
            right (): Height of another widget on the left to anchor properly

        Returns:

        """
        ...

    def icon(self, icon: str, size: int = 8,
             x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
             anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False):
        """
        Draw icon of given size.

        Args:
            icon (): The name of the icon
            size (): The font size

            x (): The x coordinate on which to start
            y (): The y coordinate on which to start
            inverse (): If inverse colour and background will be swapped
            colour (): The colour of the text
            background (): The colour of the background otherwise will be display's background

            anchor (): **To anchor:** The anchor (3x3 matrix)
            wf (): **To anchor:** The width if specified otherwise use the display's width if display otherwise the size
            hf (): **To anchor:** The height if specified otherwise use the display's height if display otherwise the size
            full (): **To anchor:** Whether to use the display dimension if no width and height specified otherwise use size

        Returns:

        """
        ...

