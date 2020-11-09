from abc import ABC, abstractmethod, abstractstaticmethod


class Plugin(ABC):
    @abstractmethod
    def run(self, data):
        pass
