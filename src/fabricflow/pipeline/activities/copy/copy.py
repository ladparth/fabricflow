"""
Microsoft Fabric Copy Activity builder and executor.

This module provides the Copy class for building and executing copy activities
in Microsoft Fabric data pipelines. Copy activities are the primary mechanism
for moving and transforming data between different sources and destinations
within the Fabric ecosystem.

Classes:
    Copy: Builder class for creating and executing copy activities with fluent API.

The Copy activity supports a wide range of data movement scenarios including:
- SQL Server to Lakehouse table transfers
- SQL Server to Parquet file exports
- Batch processing with ForEach loops
- Custom parameterization and data transformation
- Automatic query timeout and isolation level handling

Key Features:
- Fluent builder pattern for intuitive configuration
- Type-safe source and sink configuration
- Support for both single-item and batch operations
- Automatic parameter validation and error handling
- Comprehensive execution monitoring and result extraction
- Template-based pipeline creation and execution

Data Flow Patterns:
1. Single Item Copy: One source query → One destination
2. Batch Copy: Multiple items with ForEach loop processing
3. Parameterized Copy: Dynamic queries with runtime parameters

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.pipeline.activities import Copy
    from fabricflow.pipeline.sources import SQLServerSource
    from fabricflow.pipeline.sinks import LakehouseTableSink
    from fabricflow.pipeline.templates import DataPipelineTemplates

    client = FabricRestClient()

    # Create source and sink
    source = SQLServerSource(
        source_connection_id="sql-conn-123",
        source_database_name="AdventureWorks",
        source_query="SELECT * FROM Sales.Customer"
    )

    sink = LakehouseTableSink(
        sink_workspace="analytics-workspace",
        sink_lakehouse="sales-lakehouse",
        sink_table_name="customers",
        sink_schema_name="dbo",
        sink_table_action="Overwrite"
    )

    # Execute single copy operation
    copy = Copy(client, "MyWorkspace", DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE)
    result = copy.source(source).sink(sink).execute()

    # Execute batch copy operation
    items = [
        {
            "source_query": "SELECT * FROM Sales.Customer",
            "sink_table_name": "customers",
            "sink_schema_name": "sales",
            "sink_table_action": "Overwrite"
        },
        {
            "source_query": "SELECT * FROM Sales.SalesOrderHeader",
            "sink_table_name": "orders",
            "sink_schema_name": "sales",
            "sink_table_action": "Append"
        }
    ]

    batch_copy = Copy(client, "MyWorkspace", DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH)
    result = batch_copy.source(source).sink(sink).items(items).execute()
    ```

Performance Considerations:
- Use batch operations for multiple related copies to reduce overhead
- Configure appropriate query timeouts for large data transfers
- Consider isolation levels impact on source database performance
- Monitor pipeline execution for optimization opportunities

Dependencies:
- sempy.fabric: For FabricRestClient integration
- fabricflow.pipeline.templates: For pipeline template definitions
- fabricflow.pipeline.sources: For source configuration
- fabricflow.pipeline.sinks: For sink configuration
"""

from typing import Optional, Any
from sempy.fabric import FabricRestClient

from ...templates import DataPipelineTemplates
from ...sources.base import BaseSource
from ...sinks.base import BaseSink
from .executor import CopyActivityExecutor
import json


class Copy:
    """
    Builder class for creating and executing copy activities in Microsoft Fabric data pipelines.

    This class provides a fluent interface for configuring copy operations that move data
    between various sources and destinations within Microsoft Fabric. It supports both
    single-item and batch copy operations with comprehensive parameter validation and
    execution monitoring.

    The Copy class uses a builder pattern where you configure the source, sink, and
    optional parameters through method chaining, then execute the copy operation.
    It automatically handles parameter validation, payload construction, and pipeline
    execution with proper error handling.

    Key Features:
    - Fluent builder API for intuitive configuration
    - Support for single and batch copy operations
    - Automatic parameter validation and error handling
    - Template-based pipeline execution
    - Query timeout and isolation level management
    - Comprehensive execution monitoring and result extraction

    Attributes:
        workspace (str): Target workspace name or ID.
        pipeline (str): Target pipeline name or ID (resolved from template if provided).
        client (FabricRestClient): Authenticated Fabric REST client.
        default_poll_timeout (int): Default timeout for pipeline execution polling.
        default_poll_interval (int): Default interval between polling attempts.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client for API interactions.
        workspace (str): Name or ID of the target Fabric workspace.
        pipeline (str | DataPipelineTemplates): Pipeline name, ID, or template enum.
                                               If DataPipelineTemplates enum is provided,
                                               the template value will be used as pipeline name.
        default_poll_timeout (int): Default timeout in seconds for polling execution status.
                                   Defaults to 300 seconds (5 minutes).
        default_poll_interval (int): Default interval in seconds between status checks.
                                    Defaults to 15 seconds.

    Raises:
        TypeError: If client is not a FabricRestClient instance.
        ValueError: If workspace or pipeline cannot be resolved.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.pipeline.activities import Copy
        from fabricflow.pipeline.sources import SQLServerSource
        from fabricflow.pipeline.sinks import LakehouseTableSink
        from fabricflow.pipeline.templates import DataPipelineTemplates

        client = FabricRestClient()

        # Configure source and sink
        source = SQLServerSource(
            source_connection_id="sql-conn-123",
            source_database_name="AdventureWorks",
            source_query="SELECT * FROM Sales.Customer WHERE ModifiedDate > '2023-01-01'"
        )

        sink = LakehouseTableSink(
            sink_workspace="analytics-workspace",
            sink_lakehouse="sales-lakehouse",
            sink_table_name="customers",
            sink_schema_name="dbo",
            sink_table_action="Overwrite"
        )

        # Execute copy operation
        copy = Copy(
            client,
            "MyWorkspace",
            DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE
        )

        result = copy.source(source).sink(sink).execute()
        print(f"Copy completed with status: {result['status']}")

        # For batch operations
        items = [
            {
                "source_query": "SELECT * FROM Sales.Customer",
                "sink_table_name": "customers",
                "sink_schema_name": "sales",
                "sink_table_action": "Overwrite"
            },
            {
                "source_query": "SELECT * FROM Sales.SalesOrderHeader",
                "sink_table_name": "orders",
                "sink_schema_name": "sales",
                "sink_table_action": "Append"
            }
        ]

        batch_result = copy.items(items).execute()
        ```

    Note:
        - Both source and sink must be configured before calling execute()
        - For batch operations, use items() to provide multiple copy configurations
        - Query timeout and isolation level are automatically managed from source configuration
        - The class maintains backward compatibility with the previous CopyManager name
    """

    def __init__(
        self,
        client: FabricRestClient,
        workspace: str,
        pipeline: str | DataPipelineTemplates,
        default_poll_timeout: int = 300,
        default_poll_interval: int = 15,
    ) -> None:
        self.workspace = workspace

        if isinstance(pipeline, DataPipelineTemplates):
            self.pipeline = pipeline.value
        else:
            self.pipeline = pipeline

        self.client = client
        self._source: Optional[BaseSource] = None
        self._sink: Optional[BaseSink] = None
        self._extra_params: dict = {}
        self._payload = {"executionData": {"parameters": {}}}
        self.default_poll_timeout = default_poll_timeout
        self.default_poll_interval = default_poll_interval

    def source(self, source: BaseSource) -> "Copy":
        """
        Sets the source for the copy activity.
        Args:
            source (BaseSource): The source object (with source_*-prefixed params).
        Returns:
            Copy: The builder instance.
        """
        self._source = source
        return self

    def sink(self, sink: BaseSink) -> "Copy":
        """
        Sets the sink for the copy activity.
        Args:
            sink (BaseSink): The sink object (with sink_*-prefixed params).
        Returns:
            Copy: The builder instance.
        """
        self._sink = sink
        return self

    def params(self, **kwargs) -> "Copy":
        """
        Sets additional parameters for the copy activity.
        Args:
            **kwargs: Additional parameters to set.
        Returns:
            Copy: The builder instance.
        """
        self._extra_params.update(kwargs)
        return self

    def items(self, items: list[dict]) -> "Copy":
        """
        Sets additional parameters for the copy activity using items.
        Args:
            items (list): A list of dicts, each containing all required source_*/sink_* keys.
        Returns:
            Copy: The builder instance.
        Raises:
            ValueError: If any item is missing required keys.
        """

        if self._source is None or self._sink is None:
            raise ValueError("Both source and sink must be set before setting items.")
        required_keys: list[str] = (
            self._source.required_params + self._sink.required_params
        )
        for item in items:
            if not all(key in item for key in required_keys):
                raise ValueError(
                    f"Each item must contain the following keys: {required_keys}"
                )
            source_dict = self._source.to_dict()
            if "query_timeout" in source_dict:
                item["query_timeout"] = source_dict["query_timeout"]

            if "isolation_level" not in item:
                item["isolation_level"] = None

        self._extra_params["items"] = items
        return self

    def build(self) -> "Copy":
        """
        Builds the copy activity parameters.
        Returns:
            Copy: The builder instance with payload ready for execution.
        Raises:
            ValueError: If source or sink is not set.
        """
        if self._source is None or self._sink is None:
            raise ValueError(
                "Both source and sink must be set before building parameters."
            )
        params: dict[str, Any] = {
            **self._source.to_dict(),
            **self._sink.to_dict(),
            **self._extra_params,
        }
        self._payload["executionData"]["parameters"] = params
        return self

    def execute(self) -> dict:
        """
        Executes the copy activity with the built parameters.
        Returns:
            dict: Pipeline execution result (pipeline_id, status, activity_data).
        """
        # Build the payload if not already done
        if not self._payload["executionData"]["parameters"]:
            self.build()

        result: dict[str, Any] = CopyActivityExecutor(
            client=self.client,
            workspace=self.workspace,
            pipeline=self.pipeline,
            payload=self._payload,
            default_poll_timeout=self.default_poll_timeout,
            default_poll_interval=self.default_poll_interval,
        ).run()

        return result

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the Copy object to a dictionary representation.
        This includes the workspace, pipeline, source, sink, and extra parameters.

        Returns:
            dict: Dictionary representation of the Copy object.
        """
        return {
            "workspace": self.workspace,
            "pipeline": self.pipeline,
            "payload": self._payload,
        }

    def __str__(self) -> str:
        """

        Returns a JSON string representation of the Copy object.
        This includes the workspace, pipeline, source, sink, and extra parameters.

        """

        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Copy object.
        """
        return self.__str__()
