from abc import ABC, abstractmethod


class Console(ABC):
    @abstractmethod
    def main(self, *args, **kwargs):
        pass