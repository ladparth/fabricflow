"""
Microsoft Fabric Lookup Activity builder and executor.

This module provides the Lookup class for building and executing lookup activities
in Microsoft Fabric data pipelines. Lookup activities are used to retrieve data
from sources for use in pipeline logic and data transformation operations.

Classes:
    Lookup: Builder class for creating and executing lookup activities.

The Lookup activity supports both single and batch lookup operations, with
parameterization support for dynamic queries and flexible source configuration.

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.pipeline.activities import Lookup
    from fabricflow.pipeline.sources import SQLServerSource
    from fabricflow.pipeline.templates import LOOKUP_SQL_SERVER

    client = FabricRestClient()
    source = SQLServerSource(
        source_connection_id="conn123",
        source_database_name="AdventureWorks",
        source_query="SELECT TOP 1 * FROM Sales.Customer"
    )

    lookup = Lookup(client, "MyWorkspace", LOOKUP_SQL_SERVER)
    result = lookup.source(source).execute()
    ```
"""

from typing import Optional, Any
from sempy.fabric import FabricRestClient

from ...templates import DataPipelineTemplates
from ...sources.base import BaseSource
from .executor import LookupActivityExecutor
import json


class Lookup:
    """
    Builder class for creating and executing lookup activities in Microsoft Fabric pipelines.

    This class provides a fluent interface for configuring lookup activities that retrieve
    data from various sources. Lookups are commonly used to fetch reference data, validate
    values, or retrieve configuration parameters needed by other pipeline activities.

    The class supports both single-item and batch lookup operations, with flexible
    parameterization through the items() method for dynamic query execution.

    Attributes:
        workspace (str): Target workspace name or ID.
        pipeline (str): Target pipeline name or ID.
        client (FabricRestClient): Authenticated Fabric REST client.
        default_poll_timeout (int): Default timeout for pipeline execution polling.
        default_poll_interval (int): Default interval between polling attempts.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client for API interactions.
        workspace (str): Name or ID of the target Fabric workspace.
        pipeline (str | DataPipelineTemplates): Name, ID, or template enum of the pipeline.
        default_poll_timeout (int): Default timeout in seconds for polling execution status.
        default_poll_interval (int): Default interval in seconds between status checks.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.pipeline.activities import Lookup
        from fabricflow.pipeline.sources import SQLServerSource
        from fabricflow.pipeline.templates import LOOKUP_SQL_SERVER

        client = FabricRestClient()

        # Create lookup activity
        lookup = Lookup(
            client,
            "MyWorkspace",
            LOOKUP_SQL_SERVER
        )

        # Configure source
        source = SQLServerSource(
            source_connection_id="conn123",
            source_database_name="AdventureWorks",
            source_query="SELECT COUNT(*) as RecordCount FROM Sales.Customer"
        )

        # Execute lookup
        result = lookup.source(source).execute()
        print(f"Lookup result: {result}")
        ```

    Note:
        Lookup activities are read-only operations and do not modify data.
        Use Copy activities for data movement and transformation operations.
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
        self._extra_params: dict = {}
        self._payload = {"executionData": {"parameters": {}}}
        self.default_poll_timeout = default_poll_timeout
        self.default_poll_interval = default_poll_interval

    def source(self, source: BaseSource) -> "Lookup":
        """
        Set the data source for the lookup activity.

        Configures the source from which the lookup activity will retrieve data.
        The source must be a concrete implementation of BaseSource with appropriate
        connection and query configuration.

        Args:
            source (BaseSource): The configured source object containing connection
                               details and query parameters. Must have all required
                               parameters set or they will be provided via items().

        Returns:
            Lookup: The lookup builder instance for method chaining.

        Example:
            ```python
            from fabricflow.pipeline.sources import SQLServerSource

            source = SQLServerSource(
                source_connection_id="conn123",
                source_database_name="AdventureWorks",
                source_query="SELECT TOP 1 CustomerID FROM Sales.Customer"
            )

            lookup = lookup.source(source)
            ```
        """
        self._source = source
        return self

    def params(self, **kwargs) -> "Lookup":
        """
        Set additional parameters for the lookup activity execution.

        Allows setting custom parameters that will be passed to the pipeline
        execution payload. These parameters can be used for dynamic configuration
        or to override default values.

        Args:
            **kwargs: Arbitrary keyword arguments to include in the execution payload.
                     Common parameters include timeout settings, retry policies, etc.

        Returns:
            Lookup: The lookup builder instance for method chaining.

        Example:
            ```python
            lookup = lookup.params(
                execution_timeout="00:05:00",
                retry_count=3,
                custom_parameter="value"
            )
            ```
        """
        self._extra_params.update(kwargs)
        return self

    def items(self, items: list[dict]) -> "Lookup":
        """
        Configure multiple lookup operations using a list of parameter dictionaries.

        This method enables batch lookup operations where each item in the list
        represents a separate lookup with its own parameters. Useful for scenarios
        where you need to perform multiple related lookups in a single pipeline run.

        Each item dictionary must contain all required source parameters. The method
        automatically populates common parameters like query_timeout and isolation_level
        from the source configuration when not explicitly provided.

        Args:
            items (list[dict]): List of dictionaries, each containing lookup parameters.
                              Each dictionary must include all required keys from
                              the source's required_params property.

        Returns:
            Lookup: The lookup builder instance for method chaining.

        Raises:
            ValueError: If source is not set or if any item is missing required keys.

        Example:
            ```python
            items = [
                {
                    "source_query": "SELECT * FROM Sales.Customer WHERE CustomerID = 1",
                },
                {
                    "source_query": "SELECT * FROM Sales.Customer WHERE CustomerID = 2",
                }
            ]

            lookup = lookup.items(items)
            ```

        Note:
            Items will inherit query_timeout, isolation_level, and first_row_only
            settings from the source configuration if not explicitly provided.
        """

        if self._source is None:
            raise ValueError("Source must be set before setting items.")
        required_keys: list[str] = self._source.required_params.copy()

        source_dict = self._source.to_dict()
        for item in items:

            if not all(key in item for key in required_keys):
                raise ValueError(
                    f"Each item must contain the following keys: {required_keys}"
                )

            if "query_timeout" in source_dict:
                item["query_timeout"] = source_dict["query_timeout"]

            if "isolation_level" not in item:
                item["isolation_level"] = None

            if "first_row_only" not in item:
                item["first_row_only"] = False

        self._extra_params["items"] = items
        return self

    def build(self) -> "Lookup":
        """
        Builds the lookup activity parameters.
        Returns:
            Lookup: The builder instance with payload ready for execution.
        Raises:
            ValueError: If source is not set.
        """
        if self._source is None:
            raise ValueError("Source must be set before building parameters.")

        # Ensure 'first_row_only' is present; default to False if missing
        source_dict = self._source.to_dict()
        if "first_row_only" not in source_dict:
            source_dict["first_row_only"] = False

        params: dict[str, Any] = {
            **source_dict,
            **self._extra_params,
        }
        self._payload["executionData"]["parameters"] = params
        return self

    def execute(self) -> dict:
        """
        Executes the lookup activity with the built parameters.
        Returns:
            dict: Pipeline execution result (pipeline_id, status, activity_data).
        """
        # Build the payload if not already done
        if not self._payload["executionData"]["parameters"]:
            self.build()

        result: dict[str, Any] = LookupActivityExecutor(
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
        Converts the Lookup object to a dictionary representation.
        This includes the workspace, pipeline, source, and extra parameters.

        Returns:
            dict: Dictionary representation of the Lookup object.
        """
        return {
            "workspace": self.workspace,
            "pipeline": self.pipeline,
            "payload": self._payload,
        }

    def __str__(self) -> str:
        """
        Returns a JSON string representation of the Lookup object.
        This includes the workspace, pipeline, source, and extra parameters.
        """
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Lookup object.
        """
        return self.__str__()
