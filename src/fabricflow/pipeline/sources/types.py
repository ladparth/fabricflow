"""
Type definitions for Microsoft Fabric data pipeline sources.

This module defines enums and type constants used throughout the pipeline
sources system. These types ensure consistency and provide clear interfaces
for configuring data sources.

Classes:
    SourceType: Enum defining supported data source types.
    IsolationLevel: Enum defining SQL transaction isolation levels.

Example:
    ```python
    from fabricflow.pipeline.sources import SourceType, IsolationLevel

    # Use in source configuration
    source_type = SourceType.SQL_SERVER
    isolation = IsolationLevel.READ_COMMITTED
    ```
"""

from enum import Enum


class SourceType(Enum):
    """
    Enumeration of supported data source types for Microsoft Fabric pipelines.

    This enum defines the different types of data sources that can be used
    in data pipeline activities. Each source type corresponds to a specific
    connector and configuration pattern.

    Values:
        SQL_SERVER: Microsoft SQL Server database source.
                   Used for reading data from SQL Server instances.

    Example:
        ```python
        from fabricflow.pipeline.sources import SourceType

        # Use in source configuration
        if source_type == SourceType.SQL_SERVER:
            # Configure SQL Server specific settings
            pass
        ```
    """

    SQL_SERVER = "SQLServer"


class IsolationLevel(Enum):
    """
    Enumeration of SQL transaction isolation levels for database sources.

    This enum defines the available isolation levels that can be used when
    reading data from SQL database sources. Isolation levels control how
    transaction locking and row versioning are handled during data access.

    Values:
        READ_COMMITTED: Default isolation level. Prevents dirty reads but allows
                       non-repeatable reads and phantom reads.
        READ_UNCOMMITTED: Lowest isolation level. Allows dirty reads,
                         non-repeatable reads, and phantom reads.
        REPEATABLE_READ: Prevents dirty reads and non-repeatable reads but
                        allows phantom reads.
        SERIALIZABLE: Highest isolation level. Prevents all phenomena including
                     dirty reads, non-repeatable reads, and phantom reads.
        SNAPSHOT: Uses row versioning to provide statement-level read consistency
                 without blocking writers.

    Example:
        ```python
        from fabricflow.pipeline.sources import IsolationLevel

        # Use with SQL Server source
        isolation = IsolationLevel.READ_COMMITTED
        source = SQLServerSource(
            ...,
            isolation_level=isolation
        )
        ```

    Note:
        Not all isolation levels are supported by all database systems.
        Check your database documentation for supported isolation levels.
    """

    READ_COMMITTED = "ReadCommitted"
    READ_UNCOMMITTED = "ReadUncommitted"
    REPEATABLE_READ = "RepeatableRead"
    SERIALIZABLE = "Serializable"
    SNAPSHOT = "Snapshot"
