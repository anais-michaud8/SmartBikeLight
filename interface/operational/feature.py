

# Memory
import gc
gc.collect()

# Built-in
import asyncio

# Local -> Interface
from interface.basic.logger import Logging
from interface.operational.triggers import Refresher
from interface.operational.special import Input


class Feature:

    def __init__(self, name: str = None, is_logging: bool = None, style: str = None,
                 initiate_first_action: bool = True, to_refresh: list = None, to_initiate: list | None = None):
        self.to_refresh: list[Refresher] = [] if to_refresh is None else to_refresh
        self.logging = Logging(name, is_logging, self, style=style)
        if initiate_first_action:
            if not isinstance(to_initiate, list):
                to_initiate = self.to_refresh
            for refresher in to_initiate:
                if refresher is not None and hasattr(refresher, 'update'):
                    refresher.update()

    async def refresh(self):
        ...

    async def refreshing(self):
        tasks = [asyncio.create_task(self.refresh())]
        for refresher in self.to_refresh:
            is_empty = hasattr(refresher, "source") and isinstance(getattr(refresher, "source"), Input)
            if not is_empty and refresher is not None and hasattr(refresher, 'refreshing'):
                tasks.append(asyncio.create_task(refresher.refreshing()))
        await asyncio.gather(*tasks)


gc.collect()

