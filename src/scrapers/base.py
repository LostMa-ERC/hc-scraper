from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseScraperClass(ABC):
    @abstractmethod
    def validate(self) -> BaseModel:
        pass
