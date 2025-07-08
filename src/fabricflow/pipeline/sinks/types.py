"""
Type definitions for Microsoft Fabric data pipeline sinks.

This module defines enums and type constants used throughout the pipeline
sinks system. These types ensure consistency and provide clear interfaces
for configuring data destinations.

Classes:
    SinkType: Enum defining supported data sink types.

Example:
    ```python
    from fabricflow.pipeline.sinks import SinkType

    # Use in sink configuration
    sink_type = SinkType.LAKEHOUSE_TABLE
    ```
"""

from enum import Enum


class SinkType(Enum):
    """
    Enumeration of supported data sink types for Microsoft Fabric pipelines.

    This enum defines the different types of data destinations that can be used
    in data pipeline activities. Each sink type corresponds to a specific
    storage system and configuration pattern.

    Values:
        LAKEHOUSE_TABLE: Microsoft Fabric Lakehouse table destination.
                        Used for writing data to managed tables in a Lakehouse.
        PARQUET_FILE: Parquet file destination in Lakehouse Files.
                     Used for writing data to Parquet files in the Files area.

    Example:
        ```python
        from fabricflow.pipeline.sinks import SinkType

        # Use in sink configuration
        if sink_type == SinkType.LAKEHOUSE_TABLE:
            # Configure table-specific settings
            pass
        elif sink_type == SinkType.PARQUET_FILE:
            # Configure file-specific settings
            pass
        ```

    Note:
        Additional sink types may be added in future versions to support
        other Microsoft Fabric storage options and external destinations.
    """

    LAKEHOUSE_TABLE = "LakehouseTable"
    PARQUET_FILE = "ParquetFile"
