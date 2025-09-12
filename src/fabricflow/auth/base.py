"""Base class for auth token providers."""

from abc import ABC, abstractmethod
from typing import Literal


class BaseTokenProvider(ABC):
    """
    Abstract base class for logic that acquires auth tokens.
    """

    @abstractmethod
    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi") -> str:
        """
        Get implementation specific token.

        Parameters
        ----------
        audience : Literal["pbi", "storage", "sql"], optional
            The audience for which the token is requested.
            Defaults to "pbi".
        Returns
        -------
        str
            Auth token.
        """
        pass
