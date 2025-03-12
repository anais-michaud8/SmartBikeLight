
import gc
gc.collect()

import asyncio

from interface.operational.triggers import Action
from interface.display.display import Display, Colours, Colour, Font


async def reader(callback, instance: object, attr: str | None = "value", wait: float=1):
    last = None
    while True:
        if isinstance(attr, str):
            val = getattr(instance, attr)
            if last != val:
                last = val
                callback(val)
        else:
            callback(instance)
        await asyncio.sleep(wait)


async def waiter(callback, instance: object, attr: str | None = "value", wait: str = "event"):
    to_wait = getattr(instance, wait)
    while True:
        await to_wait.wait()
        callback(instance if not isinstance(attr, str) else getattr(instance, attr))
        to_wait.clear()


def action(callback, instance: Action, attr: str | None = "value", dynamic=None):
    def func(_=None, **kwargs):
        callback(instance if not isinstance(attr, str) else getattr(instance, getattr(dynamic, attr) if dynamic is not None else attr))
    instance.add(funcs=func)


gc.collect()

# =========================== #
#           Widgets           #
# =========================== #


class Widget:
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 wb: int | None = None, hb: int | None = None, border: Colour | None = None, thickness: int = 1, margin: int = 0,
         ):
        # Display
        self.display = display

        # Dimensions
        self.wf = wf
        self.hf = hf

        # Position and colours
        self.x = x
        self.y = y
        self.inverse = inverse
        self.colour = colour
        self.background = background

        # Anchor
        self.anchor = anchor
        self.wf = wf if wf is not None or not full else self.wf
        self.hf = hf if hf is not None or not full else self.hf
        self.full = full

        # Border
        self.border = border
        self.margin = margin
        self.thickness = thickness
        self.wb = wb
        self.hb = hb

    @property
    def extra(self):
        return self.margin + self.thickness if self.border else 0

    @property
    def width(self):
        """ Minimum width. """
        return self.wf

    @property
    def height(self):
        """ Minimum height. """
        return self.hf

    def show(self):
        self.display.fill(
            w=self.wf, h=self.hf, x=self.x, y=self.y, inverse=self.inverse, colour=self.background,
            anchor=self.anchor, wf=self.wf, hf=self.hf, full=self.full
        )
        if self.border is not None:
            self.display.outline(
                w=self.wb, h=self.hb, fill=False, thickness=self.thickness,
                x=self.x, y=self.y, inverse=self.inverse, colour=self.border, background=self.background,
                anchor=self.anchor, wf=self.wf, hf=self.hf, full=self.full
            )

    def hide(self):
        if self.wf and self.hf:
            self.display.fill(w=self.wf, h=self.hf, x=self.x, y=self.y)

    def setup(self):
        extra = (self.margin + self.thickness)*2 if self.border is not None else 0
        self.wf = self.width + extra if self.width is not None else None
        self.hf = self.height + extra if self.height is not None else None
        self.wb = self.wf if self.wb is None else self.wb
        self.hb = self.hf if self.hb is None else self.hb


gc.collect()


class Text(Widget):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 initial : str | int | float | bool | None = None, size: int = 8,
                 large: bool = True, bold: bool = False, underline: bool = False,
                 length: int | None = None, rounding: int = 0, converter=None, formatter: str = "{}",
                 wb: int | None = None, hb: int | None = None, border: Colour | None = None, thickness: int = 1, margin: int = 0,
                 left: int = 0, right: int = 0,
                 ):

        # Text and Font
        self.value = initial
        self.size = size
        self.large = large
        self.bold = bold
        self.underline = underline

        # Left and right
        self.left = left
        self.right = right

        # Formatting
        self.length = length
        self.rounding = rounding
        self.converter = converter
        self.formatter = formatter

        w, h = Font.get_size(size, bold, large)
        wf = (self.length * w) if wf is None and self.length is not None else wf
        hf = hf if hf is None else h + 1 if underline else h

        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            hb=hb, wb=wb, border=border, thickness=thickness, margin=margin,
        )

    def show(self):
        super().show()
        return self.display.text(
            self.value, size=self.size, large=self.large, bold=self.bold, underline=self.underline,
            length=self.length, rounding=self.rounding, converter=self.converter, formatter=self.formatter,
            x=self.x + self.extra, y=self.y + self.extra, inverse=self.inverse, colour=self.colour, background=self.background,
            anchor=self.anchor, wf=self.wb - self.extra*2, hf=self.hb - self.extra*2, full=self.full, left=self.left, right=self.right,
        )

    @property
    def width(self):
        w, _ = Font.get_size(self.size, self.bold, self.large)
        return w * self.length if self.wf is None else self.wf

    @property
    def height(self):
        _, h = Font.get_size(self.size, self.bold, self.large)
        return (h + 1 if self.underline else h) if self.hf is None else self.hf


gc.collect()


class Icon(Widget):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 initial : str | int | float | bool | None = None, size: int = 8,
                 wb: int | None = None, hb: int | None = None, border: Colour | None = None, thickness: int = 1,margin: int = 0,):
        # Icon
        self.value = initial
        self.size = size

        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            hb=hb, wb=wb, border=border, thickness=thickness, margin=margin,
        )

    def show(self):
        super().show()
        self.display.icon(
            self.value, size=self.size,
            x=self.x + self.extra, y=self.y + self.extra, inverse=self.inverse, colour=self.colour, background=self.background,
            anchor=self.anchor, wf=self.wb - self.extra*2, hf=self.hb - self.extra*2, full=self.full,
        )

    @property
    def width(self):
        return self.size if self.wf is None else self.wf

    @property
    def height(self):
        return self.size if self.hf is None else self.hf


gc.collect()


class Label(Widget):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 text: str | int | float | bool | None = None, text_size: int = 8, icon_size: int = 8, padding: int = 3,
                 prefix: str | None = None, suffix: str | int | float | bool | None = None,
                 bold: bool = False, underline: bool = False, large: bool = True,
                 length: int = 1, rounding: int = 0, converter=None, formatter: str = "{}",
                 wb: int | None = None, hb: int | None = None, border: Colour | None = None, thickness: int = 1, margin: int = 0,
                 uses_suffix: bool = False, uses_prefix: bool = False, length_includes_icons: bool = False
                 ):

        # Text and Font
        self.text = text
        self.text_size = text_size
        self.large = large
        self.bold = bold
        self.underline = underline

        # Icon
        self.icon_size = icon_size
        self.prefix = prefix
        self.suffix = suffix

        # Between
        self.padding = padding
        self.left = icon_size + self.padding
        self.right = icon_size + self.padding
        self.uses_suffix = uses_suffix
        self.uses_prefix = uses_prefix
        self.length_includes_icon = length_includes_icons

        # Formatting
        self.length = length
        self.rounding = rounding
        self.converter = converter
        self.formatter = formatter

        w, h = Font.get_size(text_size, bold, large)

        extra = (padding + 0 if self.length_includes_icon else icon_size) * (2 if uses_prefix and uses_suffix else 1 if uses_prefix or uses_suffix else 0)
        wf = (self.length * w + extra) if wf is None and self.length is not None else wf
        hf = hf if hf is None else h + 1 if underline else h

        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            hb=hb, wb=wb, border=border, thickness=thickness, margin=margin,
        )

    def show(self):
        super().show()

        x1, x2 = self.display.text(
            self.text, size=self.text_size, bold=self.bold, underline=self.underline, large=self.large,
            rounding=self.rounding, converter=self.converter, formatter=self.formatter,
            x=self.x + self.extra, y=self.y + self.extra, inverse=self.inverse, colour=self.colour, background=self.background,
            anchor=self.anchor, wf=self.wb - self.extra*2, hf=self.hb - self.extra*2, full=self.full,
            left=0 if self.prefix is None else self.left, right= 0 if self.suffix is None else self.right
        )

        if self.prefix is not None:
            self.display.icon(
                self.prefix, size=self.icon_size, x=x1, y=self.y, inverse=self.inverse,
                colour=self.colour, background=self.background, anchor=self.anchor, full=self.full, hf=self.hb - self.extra*2,
            )
        if self.suffix is not None:
            self.display.icon(
                self.suffix, size=self.icon_size, x=x2 + self.padding, y=self.y, inverse=self.inverse,
                colour=self.colour, background=self.background, anchor=self.anchor, full=self.full, hf=self.hb - self.extra*2,
            )

    @property
    def width(self):
        w, _ = Font.get_size(self.text_size, self.bold, self.large)
        extra = (self.padding + 0 if self.length_includes_icon else self.icon_size) * (2 if self.uses_prefix and self.uses_suffix
                                                   else 1 if self.uses_prefix or self.uses_suffix else 0)
        return (self.length * w + extra) if self.wf is None and self.length is not None else self.wf

    @property
    def height(self):
        _, h = Font.get_size(self.text_size, self.bold, self.large)
        return (h + 1 if self.underline else h) if h > self.icon_size \
            else self.icon_size if self.hf is None else self.hf


gc.collect()


# =========================== #
#           Dividers          #
# =========================== #


class Divider(Widget):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 length: int | None = None, thickness: int = 1, vertical: bool = False, margin: int = 0,):
        self.length = length
        self.vertical = vertical

        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            thickness=thickness, margin=margin,
        )

    @property
    def width(self):
        return self.thickness if self.vertical else self.length

    @property
    def height(self):
        return self.length if self.vertical else self.thickness

    def show(self):
        super().show()
        self.display.line(
            length=self.length, thickness=self.thickness, vertical=self.vertical,
            x=self.x, y=self.y, colour=self.colour, inverse=self.inverse,
            anchor=self.anchor, wf=self.wf, hf=self.hf, full=self.full,
        )


gc.collect()


class Horizontal(Divider):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 length: int | None = None, thickness: int = 1, margin: int = 0,):
        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            thickness=thickness, length=length, vertical=False, margin=margin,
        )


gc.collect()


class Vertical(Divider):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 length: int | None = None, thickness: int = 1, margin: int = 0,):
        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            thickness=thickness, length=length, vertical=True, margin=margin,
        )


gc.collect()


# =========================== #
#            Layout           #
# =========================== #


class Layout(Widget):
    def __init__(self, display: Display,
                 x: int = 0, y: int = 0, inverse: bool = False, colour: Colour = Colours.WHITE, background: Colour | None = None,
                 anchor: int = 5, wf: int | None = None, hf: int | None = None, full: bool = False,
                 wb: int | None = None, hb: int | None = None, border: Colour | None = None, thickness: int = 1, margin: int = 0,
                 controls: list[Widget] = None, pad_x: int | None = None, pad_y: int | None = None):
        # Controls and padding
        self.controls = controls if controls is not None else []
        self.pad_x = pad_x
        self.pad_y = pad_y

        super().__init__(
            display, x=x, y=y, inverse=inverse, colour=colour, background=background,
            anchor=anchor, wf=wf, hf=hf, full=full,
            hb=hb, wb=wb, border=border, thickness=thickness, margin=margin,
        )

    @property
    def is_last(self):
        return not any([isinstance(c, Layout) for c in self.controls])

    def show(self):
        super().show()
        for child in self.controls:
            child.show()


gc.collect()


class Row(Layout):

    @property
    def width(self) -> int:
        return self.wf if self.wf else sum([c.width for c in self.controls if c.width])

    @property
    def height(self) -> int:
        return self.hf if self.hf else max([c.height for c in self.controls if c.height])

    def setup(self):
        super().setup()
        # Calculate horizontal padding
        if self.pad_x is None and self.wf is not None:
            t = self.thickness * 2 if self.border is not None else 0
            pad_x = (self.wf - t - sum([c.width for c in self.controls])) // (len(self.controls) + 1)
        elif self.pad_x is None:
            pad_x = 0
        else:
            pad_x = self.pad_x

        # Get x and y and shift if needed
        # print(f"{self.__class__.__name__}: {self.wf}, {self.hf}, {self.width}, {self.height}")
        x, y = self.display.anchor(
            self.x, self.y, self.wf, self.hf, self.wf, self.hf, self.anchor, self.full
        )
        y = y + self.thickness if self.border is not None else y
        x = x + self.thickness if self.border is not None else x

        # Get x and y of each controls
        for i, control in enumerate(self.controls):
            control.x = x
            control.y = y
            control.setup()
            if isinstance(control, Layout):
                pass
            elif isinstance(control, Divider):
                control.length = self.hf
                control.x += pad_x
                control.hf = self.hf
            else:
                # Calculate vertical padding
                if self.pad_y is None and self.hf is not None:
                    t = self.thickness * 2 if self.border is not None else 0
                    pad_y = (self.hf - t - control.hf) // 2
                elif self.pad_y is None:
                    pad_y = 0
                else:
                    pad_y = self.pad_y

                control.y += pad_y
                control.x += pad_x
            x = control.x + control.wf


gc.collect()


class Column(Layout):

    @property
    def width(self) -> int:
        return self.wf if self.wf else max([c.width for c in self.controls if c.width])

    @property
    def height(self) -> int:
        return self.hf if self.hf else sum([c.height for c in self.controls if c.height])

    def setup(self):
        super().setup()
        # Calculate vertical padding
        if self.pad_y is None and self.hf is not None:
            t = self.thickness*2 if self.border is not None else 0
            pad_y = (self.hf - t - sum([c.height for c in self.controls])) // (len(self.controls)+1)
        elif self.pad_y is None:
            pad_y = 0
        else:
            pad_y = self.pad_y

        # Get x and y and shift if needed
        # print(f"{self.__class__.__name__}: {self.wf}, {self.hf}, {self.width}, {self.height}")
        x, y = self.display.anchor(
            self.x, self.y, self.wf, self.hf, self.wf, self.hf, self.anchor, self.full
        )
        y = y + self.thickness if self.border is not None else y
        x = x + self.thickness if self.border is not None else x

        # Get x and y of each controls
        for i, control in enumerate(self.controls):
            control.x = x
            control.y = y
            control.setup()
            if isinstance(control, Layout):
                pass
            elif isinstance(control, Divider):
                control.length = self.wf
                control.y += pad_y
                control.wf = self.wf
            else:
                # Calculate vertical padding
                if self.pad_x is None and self.wf is not None:
                    t = self.thickness * 2 if self.border is not None else 0
                    pad_x = (self.wf - t - control.wf) // 2
                elif self.pad_x is None:
                    pad_x = 0
                else:
                    pad_x = self.pad_x

                control.x += pad_x
                control.y += pad_y
            y = control.y + control.hf


gc.collect()
