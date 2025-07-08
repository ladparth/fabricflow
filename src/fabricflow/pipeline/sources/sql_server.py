"""
Microsoft SQL Server data source implementation for Fabric data pipelines.

This module provides the SQLServerSource class, which implements the BaseSource
interface for reading data from Microsoft SQL Server databases in Microsoft Fabric
data pipelines. It supports advanced SQL Server features including transaction
isolation levels, query timeouts, and flexible query execution patterns.

Classes:
    SQLServerSource: Concrete implementation of BaseSource for SQL Server databases.

The SQLServerSource class provides comprehensive support for SQL Server data access
within Microsoft Fabric pipelines, including both Copy and Lookup activities. It
handles connection management, query execution parameters, and transaction control
with proper validation and error handling.

Key Features:
- SQL Server connection and database targeting
- Configurable transaction isolation levels
- Query timeout management with timespan format
- Support for both Copy and Lookup activity patterns
- Flexible query parameterization (immediate or deferred)
- Comprehensive parameter validation and error handling
- First-row-only mode for lookup operations

Supported Scenarios:
- Single table/view extraction for Copy activities
- Complex JOIN queries with filtering and transformations
- Lookup operations for reference data retrieval
- Batch processing with dynamic query parameterization
- Transaction-aware data extraction with isolation control

Example:
    ```python
    from fabricflow.pipeline.sources import SQLServerSource
    from fabricflow.pipeline.sources import IsolationLevel
    
    # Basic source configuration for copy operations
    source = SQLServerSource(
        source_connection_id="sql-server-conn-123",
        source_database_name="AdventureWorks2022",
        source_query="SELECT * FROM Sales.Customer WHERE ModifiedDate > '2023-01-01'",
        query_timeout="01:30:00"  # 90 minutes
    )
    
    # Advanced configuration with isolation level
    advanced_source = SQLServerSource(
        source_connection_id="sql-server-conn-123", 
        source_database_name="AdventureWorks2022",
        source_query="SELECT c.*, a.City FROM Sales.Customer c JOIN Person.Address a ON c.CustomerID = a.AddressID",
        isolation_level=IsolationLevel.READ_COMMITTED,
        query_timeout="02:00:00"
    )
    
    # Lookup source for reference data (first row only)
    lookup_source = SQLServerSource(
        source_connection_id="sql-server-conn-123",
        source_database_name="AdventureWorks2022", 
        source_query="SELECT COUNT(*) as TotalCustomers FROM Sales.Customer",
        first_row_only=True,
        query_timeout="00:05:00"  # 5 minutes for quick lookup
    )
    
    # Batch processing source (query provided via items)
    batch_source = SQLServerSource(
        source_connection_id="sql-server-conn-123",
        source_database_name="AdventureWorks2022"
        # source_query will be provided in items list for batch operations
    )
    ```

Performance Considerations:
- Use appropriate isolation levels to balance consistency and performance
- Set reasonable query timeouts based on expected data volume
- Consider indexing strategies for optimal query performance
- Use READ_UNCOMMITTED for non-critical reporting queries to reduce blocking

Security Notes:
- Connection IDs should reference properly secured SQL Server connections
- Isolation levels affect locking behavior and concurrent access patterns
- Query timeouts help prevent runaway queries from consuming resources

Dependencies:
- fabricflow.pipeline.sources.base: For BaseSource interface
- fabricflow.pipeline.sources.types: For SourceType and IsolationLevel enums
"""

from .base import BaseSource
from .types import SourceType, IsolationLevel
from logging import Logger
import logging
from typing import Any, Optional

logger: Logger = logging.getLogger(__name__)


class SQLServerSource(BaseSource):
    """
    Microsoft SQL Server data source implementation for Fabric data pipelines.

    This class provides a concrete implementation of BaseSource specifically designed
    for reading data from Microsoft SQL Server databases. It supports advanced SQL Server
    features including transaction isolation levels, query timeouts, and flexible query
    execution patterns suitable for both Copy and Lookup activities.

    The SQLServerSource handles all aspects of SQL Server connectivity and query execution
    within Microsoft Fabric pipelines, including connection management, parameter validation,
    and transaction control. It supports both immediate query specification and deferred
    query provision through the items mechanism for batch operations.

    Key Features:
    - SQL Server connection and database targeting with validation
    - Configurable transaction isolation levels for data consistency control
    - Query timeout management with proper timespan format validation
    - Support for both single-query and batch query execution patterns
    - First-row-only mode specifically designed for lookup operations
    - Comprehensive parameter validation and descriptive error messages
    - Automatic logging of initialization parameters for debugging

    Use Cases:
    - Extract complete tables or filtered datasets for Copy activities
    - Execute complex analytical queries with JOINs and aggregations
    - Retrieve reference data or configuration values via Lookup activities
    - Process multiple queries in batch operations with dynamic parameterization
    - Control transaction behavior with appropriate isolation levels

    Attributes:
        source_connection_id (str): Unique identifier for the configured SQL Server connection.
        source_database_name (str): Target database name within the SQL Server instance.
        source_query (Optional[str]): SQL query to execute. Can be None for batch operations.
        first_row_only (Optional[bool]): Whether to return only the first result row (for lookups).
        isolation_level (Optional[IsolationLevel]): Transaction isolation level for query execution.
        query_timeout (Optional[str]): Query timeout in timespan format (HH:MM:SS).

    Args:
        source_connection_id (str): Unique identifier for the SQL Server connection.
                                   Must reference a valid connection configured in Fabric.
        source_database_name (str): Name of the target database within the SQL Server instance.
                                   Must be accessible through the specified connection.
        source_query (Optional[str]): SQL query to execute against the database.
                                     If None, query must be provided via items in batch operations.
        first_row_only (Optional[bool]): If True, only the first row will be returned.
                                        Primarily used with Lookup activities. Defaults to None.
        isolation_level (Optional[IsolationLevel]): Transaction isolation level for the query.
                                                   Must be a valid IsolationLevel enum value.
                                                   Defaults to None (uses connection default).
        query_timeout (Optional[str]): Query execution timeout in timespan format (HH:MM:SS).
                                      Must be a valid timespan string. Defaults to "02:00:00".

    Raises:
        ValueError: If source_connection_id or source_database_name is empty.
        ValueError: If first_row_only is not a boolean when provided.
        ValueError: If isolation_level is not a valid IsolationLevel enum value.
        ValueError: If query_timeout is not in proper timespan format (HH:MM:SS).

    Example:
        ```python
        from fabricflow.pipeline.sources import SQLServerSource
        from fabricflow.pipeline.sources import IsolationLevel

        # Basic configuration for copy operations
        copy_source = SQLServerSource(
            source_connection_id="sql-conn-production",
            source_database_name="SalesDB",
            source_query="SELECT * FROM Orders WHERE OrderDate >= '2024-01-01'",
            query_timeout="01:30:00"
        )

        # Advanced configuration with isolation level
        analytical_source = SQLServerSource(
            source_connection_id="sql-conn-analytics",
            source_database_name="DataWarehouse", 
            source_query='''
                SELECT 
                    c.CustomerID,
                    c.CustomerName,
                    SUM(o.OrderTotal) as TotalSpent
                FROM Customers c
                LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
                WHERE c.IsActive = 1
                GROUP BY c.CustomerID, c.CustomerName
                HAVING SUM(o.OrderTotal) > 10000
            ''',
            isolation_level=IsolationLevel.READ_COMMITTED,
            query_timeout="02:00:00"
        )

        # Lookup source for reference data
        lookup_source = SQLServerSource(
            source_connection_id="sql-conn-config",
            source_database_name="ConfigDB",
            source_query="SELECT ConfigValue FROM SystemConfig WHERE ConfigKey = 'MaxBatchSize'",
            first_row_only=True,
            query_timeout="00:01:00"
        )

        # Batch processing source
        batch_source = SQLServerSource(
            source_connection_id="sql-conn-etl",
            source_database_name="SourceDB"
            # Queries will be provided via items for each batch operation
        )

        # Check required parameters
        print(f"Required params: {copy_source.required_params}")
        
        # Convert to dictionary for pipeline execution
        source_config = copy_source.to_dict()
        ```

    Note:
        - Connection ID must reference a properly configured SQL Server connection in Fabric
        - Query timeout format must be HH:MM:SS (e.g., "02:30:00" for 2.5 hours)
        - Isolation levels affect concurrent access and locking behavior
        - For batch operations, source_query can be None if provided via items
        - first_row_only should only be used with Lookup activities, not Copy activities
    """

    def __init__(
        self,
        source_connection_id: str,
        source_database_name: str,
        source_query: Optional[str] = None,
        first_row_only: Optional[bool] = None,
        isolation_level: Optional[IsolationLevel] = None,
        query_timeout: Optional[str] = "02:00:00",
    ) -> None:
        super().__init__()

        if not source_connection_id:
            raise ValueError("source_connection_id cannot be empty.")
        if not source_database_name:
            raise ValueError("source_database_name cannot be empty.")
        if first_row_only is not None and not isinstance(first_row_only, bool):
            raise ValueError("first_row_only must be a boolean value.")
        if isolation_level and not isinstance(isolation_level, IsolationLevel):
            raise ValueError(
                "isolation_level must be an instance of IsolationLevel enum."
            )
        if query_timeout is not None:
            if not isinstance(query_timeout, str):
                raise ValueError(
                    "query_timeout must be a timespan string in 'HH:MM:SS' format, e.g., '02:00:00'."
                )
            parts = query_timeout.split(":")
            if len(parts) != 3 or not all(p.isdigit() for p in parts):
                raise ValueError(
                    "query_timeout must be a timespan string in 'HH:MM:SS' format, e.g., '02:00:00'."
                )

        self.source_connection_id = source_connection_id
        self.source_database_name = source_database_name
        self.source_query = source_query
        self.first_row_only = first_row_only
        self.isolation_level = isolation_level
        self.query_timeout = query_timeout

        logger.info(
            f"SQLServerSource initialized: source_connection_id='{source_connection_id}', source_database_name='{source_database_name}', source_query='{(source_query[:50] + '...') if source_query else None}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of required parameters for the SQL Server source.
        This can be overridden by subclasses to provide specific parameters.
        """
        return ["source_query"]

    def to_dict(self) -> dict[str, str]:
        """
        Converts the SQLServerSource object to a dictionary.
        Only includes 'source_query' if source_query is not empty.
        """
        result: dict[str, Any] = {
            "source_type": SourceType.SQL_SERVER.value,
            "source_connection_id": self.source_connection_id,
            "source_database_name": self.source_database_name,
        }
        if self.source_query:
            result["source_query"] = self.source_query
        if self.first_row_only is not None:
            result["first_row_only"] = self.first_row_only
        if self.isolation_level is not None:
            result["isolation_level"] = self.isolation_level.value
        if self.query_timeout is not None:
            result["query_timeout"] = self.query_timeout
        return result
