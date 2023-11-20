from abc import ABC, abstractmethod


class Collector(ABC):
    @abstractmethod
    def start(self, timeout):
        pass

    @abstractmethod
    async def get_event_stream(self):
        pass


class Strategy(ABC):
    @abstractmethod
    async def sync_state(self):
        pass

    @abstractmethod
    async def process_event(self, event):
        pass


class Executor(ABC):
    @abstractmethod
    async def execute(self, action):
        pass
