
import gc
gc.collect()


class Average:
    def __init__(self, points: int = 100):
        self.points = points
        self.data = []

    @property
    def value(self) -> float:
        return sum(self.data) / len(self.data) if len(self.data) > 0 else 0

    def collect(self, value: float):
        self.data.append(value)
        while len(self.data) >= self.points:
            self.data.pop(0)

    def __float__(self):
        return self.value

    def __call__(self, value: float):
        self.collect(value)


gc.collect()
