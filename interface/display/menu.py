
import gc
gc.collect()

# Interface -> Basic
from interface.basic.scale import Scale

# Interface -> Operational
from interface.operational.triggers import Trigger

# Interface -> Display
from interface.display.apps import Screen


class Option:

    def __init__(self, screen: Screen, setting: bool = True, title: str = "Menu", icon: str | None = None):
        self.screen = screen
        self.title = title
        self.icon = icon
        self.parent = None
        self.setting = setting

    def __str__(self):
        return self.title

    # Enter / Exit

    def enter(self):
        ...

    def exit(self):
        if self.parent is not None:
            self.parent.enter()


gc.collect()


class Selection(Option):
    _current: 'Selection' = None

    def __init__(self, screen: Screen, setting: bool = True, title: str = "Menu", icon: str | None = None,
                 iterable: tuple | list | None = None, start: int | float = 0, end: int | float = 10, step: int | float = 1,
                 initial: int | float | None = None, index: int | None = None):
        self.scale = Scale(start=start, end=end, step=step, initial=initial, iterable=iterable)
        if index is not None:
            self.index = index
        super().__init__(screen, setting=setting, title=title, icon=icon)

    @property
    def value(self):
        return self.scale.value

    @property
    def index(self):
        return self.scale.index

    @index.setter
    def index(self, value: int):
        self.scale.index = value

    # Show / Hide

    def show(self):
        if self.setting:
            if self.screen.dynamic != 0:
                self.screen.dynamic = 0
            self.screen.value(str(self.value), self.value.icon if hasattr(self.value, "icon") else None)
            self.screen.title(str(self.title), self.icon)

    # Enter / Exit

    def enter(self):
        Selection._current = self
        self.show()

    # Callbacks

    def select(self):
        self.exit()

    def cancel(self):
        self.exit()

    def prev(self):
        self.scale.down()
        if self.setting:
            self.screen.value(str(self.value), self.value.icon if hasattr(self.value, "icon") else None)

    def next(self):
        self.scale.up()
        if self.setting:
            self.screen.value(str(self.value), self.value.icon if hasattr(self.value, "icon") else None)

    # Callbacks

    @classmethod
    def callback_select(cls, _=None):
        cls._current.select()

    @classmethod
    def callback_cancel(cls, _=None):
        cls._current.cancel()

    @classmethod
    def callback_next(cls, _=None):
        cls._current.next()

    @classmethod
    def callback_prev(cls, _=None):
        cls._current.prev()


gc.collect()


class Menu(Selection):
    def __init__(self, screen: Screen, setting: bool = True, icon: str | None = None,
                 title: str = "Menu", iterable: tuple[Option, ...] = None,
                 initial: int | float | None = None, index: int | None = None):
        super().__init__(
            screen=screen, setting=setting, icon=icon,
            title=title, iterable=iterable, initial=initial, index=index
        )
        for child in iterable:
            child.parent = self

    # Callbacks

    def select(self):
        super().select()
        self.value.enter()


gc.collect()


class State(Selection):
    def __init__(self, screen: Screen, setting: bool = True, icon: str | None = None,
                 title: str = "Menu", iterable: tuple | list | None = None, trigger: Trigger | None = None,
                 start: int | float = 0, end: int | float = 10, step: int | float = 1,
                 initial: int | float | str | None = None, index: int | None = None,
                 callback=None):

        self.callback = callback
        self.trigger = trigger
        self.last = None

        super().__init__(
            screen=screen, setting=setting, icon=icon,
            title=title, iterable=iterable, start=start, end=end, step=step, initial=initial, index=index
        )

    # Enter / Exit

    def enter(self):
        super().enter()
        if self.trigger is not None:
            self.scale.value = int(self.trigger.value)
        self.last = self.scale.index

    # Callbacks

    def select(self):
        super().select()
        if self.index != self.last:
            if self.trigger is not None:
                self.trigger.set_value(self.index)
            if self.callback is not None:
                self.callback(self.value)

    def cancel(self):
        super().cancel()
        self.index = self.last


gc.collect()


class Function(Option):
    def __init__(self, screen: Screen, callback=None, title: str = "Menu", icon: str | None = None):
        self.callback = callback
        super().__init__(screen=screen, title=title, setting=True, icon=icon)

    # Enter / Exit

    def enter(self):
        self.callback()
        self.exit()


gc.collect()


class CheckBox(Option):
    def __init__(self, screen: Screen, callback=None, initial: bool = False, title: str = "Menu"):
        self.value = initial
        self.callback = callback
        super().__init__(screen=screen, title=title, setting=True, icon="checked" if self.value else "unchecked")

    # Enter / Exit

    def enter(self):
        self.value = not self.value
        self.icon = "checked" if self.value else "unchecked"
        self.callback(self.value)
        self.exit()


gc.collect()

