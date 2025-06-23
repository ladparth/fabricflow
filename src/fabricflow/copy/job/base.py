import logging
from logging import Logger
from abc import ABC, abstractmethod
from typing import Any

logger: Logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """
    Abstract base class for all data sources.
    Defines common attributes and an abstract method for conversion to dictionary.
    """

    def __init__(self) -> None:
        logger.debug(f"BaseSource initialized for {self.__class__.__name__}")

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of keys that are required parameters for the sink.
        This should be overridden by subclasses to provide specific required keys.
        """
        return []

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Abstract method to convert the source object to a dictionary.
        Subclasses must implement this method.
        """
        pass

    def __str__(self) -> str:
        """
        Returns a JSON string representation of the object using to_dict().
        """
        import json

        try:
            return json.dumps(self.to_dict(), indent=4)
        except Exception:
            return super().__str__()

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        """
        return self.__str__()


class BaseSink(ABC):
    """
    Abstract base class for all data sinks.
    Only defines the common interface (e.g., to_dict) that all sinks must implement.
    Specific attributes are handled by subclasses.
    """

    def __init__(self) -> None:
        logger.debug(f"BaseSink initialized for {self.__class__.__name__}")

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of keys that are required parameters for the sink.
        This should be overridden by subclasses to provide specific required keys.
        """
        return []

    @abstractmethod
    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Abstract method to convert the sink object to a dictionary.
        Subclasses must implement this method.
        """
        pass

    def __str__(self) -> str:
        """
        Returns a JSON string representation of the object using to_dict().
        """
        import json

        try:
            return json.dumps(self.to_dict(), indent=4)
        except Exception:
            return super().__str__()

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        """
        return self.__str__()
