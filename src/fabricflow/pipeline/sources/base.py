"""
Base classes and abstractions for Microsoft Fabric data pipeline sources.

This module provides the foundational abstract base class that all data pipeline
sources must inherit from. Sources represent the origin of data in data pipeline
operations such as copy activities and lookup activities.

Classes:
    BaseSource: Abstract base class for all data pipeline sources.

The BaseSource class enforces a consistent interface for all source implementations,
ensuring they provide the necessary methods for integration with Microsoft Fabric
data pipelines.

All concrete source implementations should inherit from BaseSource and implement
the required abstract methods. This provides a uniform way to handle different
data sources (SQL Server, Azure Storage, etc.) in pipeline activities.

Example:
    Creating a custom source:
    
    ```python
    class CustomSource(BaseSource):
        def __init__(self, connection_id: str):
            super().__init__()
            self.connection_id = connection_id
        
        @property 
        def required_params(self) -> list[str]:
            return ["source_query"]
            
        def to_dict(self) -> dict[str, Any]:
            return {"connection_id": self.connection_id}
    ```
"""

import logging
from logging import Logger
from abc import ABC, abstractmethod
from typing import Any

logger: Logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """
    Abstract base class for all data pipeline sources.
    
    This class defines the interface that all source implementations must follow.
    Sources represent the origin of data in pipeline activities and encapsulate
    the connection details, configuration, and parameters needed to read data.
    
    All concrete source classes must inherit from this base class and implement
    the required abstract methods to ensure consistent behavior across different
    source types.
    
    Attributes:
        None directly, but subclasses should define source-specific attributes.
        
    Methods:
        required_params: Abstract property that returns required parameter names.
        to_dict: Abstract method that converts source configuration to dictionary.
        
    Example:
        ```python
        # Subclass implementation
        class SQLServerSource(BaseSource):
            def __init__(self, connection_id: str, database: str):
                super().__init__()
                self.connection_id = connection_id
                self.database = database
                
            @property
            def required_params(self) -> list[str]:
                return ["source_query"]
                
            def to_dict(self) -> dict[str, Any]:
                return {
                    "source_connection_id": self.connection_id,
                    "source_database_name": self.database
                }
        ```
    """

    def __init__(self) -> None:
        """
        Initialize the base source.
        
        This constructor should be called by all subclass constructors using super().__init__().
        It provides any common initialization logic needed by all sources.
        """
        logger.debug(f"Initializing {self.__class__.__name__}")

    @property
    @abstractmethod
    def required_params(self) -> list[str]:
        """
        Abstract property that returns a list of required parameter names.
        
        This property must be implemented by all concrete source classes to specify
        which parameters are mandatory when using the source in pipeline activities.
        These parameters will be validated when building pipeline payloads.
        
        Returns:
            list[str]: List of required parameter names that must be provided
                      when using this source type.
                      
        Example:
            ```python
            @property
            def required_params(self) -> list[str]:
                return ["source_query", "source_table_name"]
            ```
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Abstract method that converts the source configuration to a dictionary.
        
        This method must be implemented by all concrete source classes to provide
        a dictionary representation of the source configuration. The dictionary
        will be used to build pipeline execution payloads.
        
        The dictionary should include all necessary configuration parameters with
        appropriate keys that match the expected pipeline parameter names.
        
        Returns:
            dict[str, Any]: Dictionary representation of the source configuration
                           with all necessary parameters for pipeline execution.
                           
        Example:
            ```python
            def to_dict(self) -> dict[str, Any]:
                return {
                    "source_type": "SQLServer",
                    "source_connection_id": self.connection_id,
                    "source_database_name": self.database_name,
                    "source_query": self.query
                }
            ```
        """
        pass
