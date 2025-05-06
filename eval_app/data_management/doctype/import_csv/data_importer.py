
from abc import ABC, abstractmethod

class DataImporter(ABC):
    @abstractmethod
    def make_stack_import(self,rows):
        pass