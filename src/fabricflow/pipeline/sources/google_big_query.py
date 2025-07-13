"""
Google BigQuery data source implementation for Fabric data pipelines.

This module provides the GoogleBigQuerySource class, which implements the BaseSource
interface for reading data from Google BigQuery datasets in Microsoft Fabric
data pipelines. It supports BigQuery-specific features including SQL query execution
and flexible data transformation patterns.

Classes:
    GoogleBigQuerySource: Concrete implementation of BaseSource for Google BigQuery.

The GoogleBigQuerySource class provides comprehensive support for BigQuery data access
within Microsoft Fabric pipelines, including both Copy and Lookup activities. It
handles connection management, query execution with proper validation and error handling.

Key Features:
- Google BigQuery connection and query execution
- Support for both Copy and Lookup activity patterns
- Flexible query parameterization (immediate or deferred)
- Comprehensive parameter validation and error handling
- Advanced BigQuery SQL capabilities and functions

Supported Scenarios:
- Large-scale dataset extraction from BigQuery for Copy activities
- Complex analytical queries with BigQuery's advanced SQL features
- Lookup operations for reference data retrieval
- Batch processing with dynamic query parameterization

Example:
    ```python
    from fabricflow.pipeline.sources import GoogleBigQuerySource

    # Basic source configuration for copy operations
    source = GoogleBigQuerySource(
        source_connection_id="bigquery-conn-id",
        source_query='''
            SELECT
                customer_id,
                order_total,
                order_date,
                CURRENT_TIMESTAMP() as extraction_timestamp,
                'bigquery_sales' as data_source
            FROM `project.dataset.orders`
            WHERE order_date >= '2024-01-01'
        '''
    )

    ```

Performance Considerations:
- Use appropriate BigQuery slot allocation for large queries
- Consider query cost optimization with proper WHERE clauses
- Leverage BigQuery's native analytics functions for better performance
- Use partitioned tables for optimal query performance

Security Notes:
- Connection IDs should reference properly secured BigQuery connections
- Ensure proper IAM permissions for dataset and table access
- Be mindful of data location and compliance requirements

Dependencies:
- fabricflow.pipeline.sources.base: For BaseSource interface
- fabricflow.pipeline.sources.types: For SourceType enum
"""

from typing import Optional, Any
from .base import BaseSource
import logging
from logging import Logger
from .types import SourceType

logger: Logger = logging.getLogger(__name__)


class GoogleBigQuerySource(BaseSource):
    """
    Google BigQuery data source implementation for Fabric data pipelines.

    This class provides a concrete implementation of BaseSource specifically designed
    for reading data from Google BigQuery datasets. It supports BigQuery's advanced
    SQL capabilities for data extraction and transformation within Microsoft Fabric pipelines.

    The GoogleBigQuerySource handles all aspects of BigQuery connectivity and query
    execution within Microsoft Fabric pipelines, including connection management,
    parameter validation, and query execution. It supports both immediate
    query specification and deferred query provision through the items mechanism
    for batch operations.

    Key Features:
    - Google BigQuery connection and query execution with validation
    - Support for both single-query and batch query execution patterns
    - Advanced BigQuery SQL functions and capabilities
    - Comprehensive parameter validation and descriptive error messages
    - Automatic logging of initialization parameters for debugging

    Use Cases:
    - Extract large datasets from BigQuery for analytical processing
    - Execute complex BigQuery SQL with advanced analytics functions
    - Retrieve reference data or configuration values via Lookup activities
    - Process multiple queries in batch operations with dynamic parameterization

    Attributes:
        source_connection_id (str): Unique identifier for the configured BigQuery connection.
        source_query (Optional[str]): BigQuery SQL query to execute. Can be None for batch operations.

    Args:
        source_connection_id (str): Unique identifier for the BigQuery connection.
                                   Must reference a valid connection configured in Fabric.
        source_query (Optional[str]): BigQuery SQL query to execute against the dataset.
                                            If None, query must be provided via items in batch operations.

    Raises:
        ValueError: If source_connection_id is empty.

    Example:
        ```python
        from fabricflow.pipeline.sources import GoogleBigQuerySource

        # Basic configuration for copy operations
        copy_source = GoogleBigQuerySource(
            source_connection_id="bigquery-prod-conn",
            source_query='''
                SELECT
                    customer_id,
                    customer_name,
                    total_orders,
                    last_order_date,
                    CURRENT_TIMESTAMP() as extraction_timestamp,
                    'production' as environment
                FROM `ecommerce.analytics.customer_summary`
                WHERE last_order_date >= '2024-01-01'
                ORDER BY total_orders DESC
            '''
        )
        ```

    Note:
        - Connection ID must reference a properly configured BigQuery connection in Fabric
        - BigQuery queries should follow standard SQL syntax with BigQuery extensions
        - Use BigQuery's built-in functions like CURRENT_TIMESTAMP(), DATE(), etc. for dynamic columns
        - For batch operations, source_query can be None if provided via items
        - Consider BigQuery query costs and slot usage for large-scale operations
    """

    def __init__(
        self,
        source_connection_id: str,
        source_query: Optional[str] = None,
        first_row_only: Optional[bool] = None,
    ) -> None:
        super().__init__()

        if not source_connection_id:
            raise ValueError("source_connection_id cannot be empty.")
        if first_row_only is not None and not isinstance(first_row_only, bool):
            raise ValueError("first_row_only must be a boolean value.")

        self.source_connection_id = source_connection_id
        self.source_query = source_query
        self.first_row_only = first_row_only

        logger.info(
            f"GoogleBigQuerySource initialized: source_connection_id='{source_connection_id}', "
            f"source_query='{(source_query[:50] + '...') if source_query else None}', "
            f"first_row_only={first_row_only}"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of required parameters for the Google BigQuery source.

        For BigQuery sources, the source_query is typically required unless
        queries are provided dynamically via items in batch operations.

        Returns:
            list[str]: List containing 'source_query' as the required parameter.
        """
        return ["source_query"]

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the GoogleBigQuerySource object to a dictionary representation.

        This method serializes the source configuration into a dictionary format
        suitable for pipeline execution. Only includes non-empty values to maintain
        clean configuration output.

        Returns:
            dict[str, Any]: Dictionary representation of the BigQuery source configuration
                          containing source type, connection ID, and optional parameters.

        Example:
            ```python
            source = GoogleBigQuerySource(
                source_connection_id="bigquery-conn",
                source_query="SELECT * FROM dataset.table"
            )
            config = source.to_dict()
            # Returns:
            # {
            #     "source_type": "GoogleBigQuery",
            #     "source_connection_id": "bigquery-conn-id",
            #     "source_query": "SELECT * FROM dataset.table"
            # }
            ```
        """
        result: dict[str, Any] = {
            "source_type": SourceType.GOOGLE_BIGQUERY.value,
            "source_connection_id": self.source_connection_id,
        }

        if self.source_query:
            result["source_query"] = self.source_query
        if self.first_row_only is not None:
            result["first_row_only"] = self.first_row_only

        return result
