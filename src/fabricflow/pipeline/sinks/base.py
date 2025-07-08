"""
Base classes and abstractions for Microsoft Fabric data pipeline sinks.

This module provides the foundational abstract base class that all data pipeline
sinks must inherit from. Sinks represent the destination where data is written
in data pipeline operations such as copy activities.

Classes:
    BaseSink: Abstract base class for all data pipeline sinks.

The BaseSink class enforces a consistent interface for all sink implementations,
ensuring they provide the necessary methods for integration with Microsoft Fabric
data pipelines.

All concrete sink implementations should inherit from BaseSink and implement
the required abstract methods. This provides a uniform way to handle different
data destinations (Lakehouse tables, Parquet files, etc.) in pipeline activities.

Example:
    Creating a custom sink:
    
    ```python
    class CustomSink(BaseSink):
        def __init__(self, target_location: str):
            super().__init__()
            self.target_location = target_location
        
        @property 
        def required_params(self) -> list[str]:
            return ["sink_table_name"]
            
        def to_dict(self) -> dict[str, Any]:
            return {"sink_location": self.target_location}
    ```
"""

import logging
from logging import Logger
from abc import ABC, abstractmethod
from typing import Any

logger: Logger = logging.getLogger(__name__)


class BaseSink(ABC):
    """
    Abstract base class for all data pipeline sinks.
    
    This class defines the interface that all sink implementations must follow.
    Sinks represent the destination where data is written in pipeline activities
    and encapsulate the connection details, configuration, and parameters needed
    to write data to the target destination.
    
    All concrete sink classes must inherit from this base class and implement
    the required abstract methods to ensure consistent behavior across different
    sink types.
    
    Attributes:
        None directly, but subclasses should define sink-specific attributes.
        
    Methods:
        required_params: Abstract property that returns required parameter names.
        to_dict: Abstract method that converts sink configuration to dictionary.
        
    Example:
        ```python
        # Subclass implementation
        class LakehouseTableSink(BaseSink):
            def __init__(self, workspace_id: str, lakehouse_id: str):
                super().__init__()
                self.workspace_id = workspace_id
                self.lakehouse_id = lakehouse_id
                
            @property
            def required_params(self) -> list[str]:
                return ["sink_table_name"]
                
            def to_dict(self) -> dict[str, Any]:
                return {
                    "sink_workspace": self.workspace_id,
                    "sink_lakehouse": self.lakehouse_id
                }
        ```
    """

    def __init__(self) -> None:
        """
        Initialize the base sink.
        
        This constructor should be called by all subclass constructors using super().__init__().
        It provides any common initialization logic needed by all sinks.
        """
        logger.debug(f"Initializing {self.__class__.__name__}")

    @property
    @abstractmethod
    def required_params(self) -> list[str]:
        """
        Abstract property that returns a list of required parameter names.
        
        This property must be implemented by all concrete sink classes to specify
        which parameters are mandatory when using the sink in pipeline activities.
        These parameters will be validated when building pipeline payloads.
        
        Returns:
            list[str]: List of required parameter names that must be provided
                      when using this sink type.
                      
        Example:
            ```python
            @property
            def required_params(self) -> list[str]:
                return ["sink_table_name", "sink_schema_name"]
            ```
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Abstract method that converts the sink configuration to a dictionary.
        
        This method must be implemented by all concrete sink classes to provide
        a dictionary representation of the sink configuration. The dictionary
        will be used to build pipeline execution payloads.
        
        The dictionary should include all necessary configuration parameters with
        appropriate keys that match the expected pipeline parameter names.
        
        Returns:
            dict[str, Any]: Dictionary representation of the sink configuration
                           with all necessary parameters for pipeline execution.
                           
        Example:
            ```python
            def to_dict(self) -> dict[str, Any]:
                return {
                    "sink_type": "LakehouseTable",
                    "sink_workspace": self.workspace_id,
                    "sink_lakehouse": self.lakehouse_id,
                    "sink_table_name": self.table_name
                }
            ```
        """
        pass
