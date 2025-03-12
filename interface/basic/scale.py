

import gc
gc.collect()

# Memory used for class Scale: 480 | Collect: 368
# Memory (average time to .up()) used for object: | With list: 32 (87us) | Without: 48 (79us)


class Scale:
    def __init__(self, start: int | float = 0, end: int | float = 10, step: int | float = 1, initial: int | float | None = None,
                 iterable: tuple | list | None = None):
        if iterable is None:
            self.start: int | float = start
            self.step: int | float = step
            self._length: int = 1 + (end - start) // step
        else:
            self.iterable: list | tuple = iterable
            # self.length: int = len(iterable)

        self._index: int = 0
        if initial is not None:
            self.value = initial

    @property
    def length(self):
        return len(self.iterable) if hasattr(self, "iterable") else self._length

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, index: int):
        self._index = index % self.length

    @property
    def value(self):
        return self.iterable[self._index] if hasattr(self, "iterable") else self.start + self._index * self.step

    @value.setter
    def value(self, value):
        if hasattr(self, "iterable"):
            try:
                self.index = self.iterable.index(value)
            except ValueError:
                print(f"Value '{value}' is not in iterable")
        else:
            div, rest = divmod(value - self.start, self.step)
            self.index = int(div) + (1 if rest >= self.step / 2 else 0)

    def up(self):
        self.index += 1

    def down(self):
        self.index -= 1


gc.collect()



