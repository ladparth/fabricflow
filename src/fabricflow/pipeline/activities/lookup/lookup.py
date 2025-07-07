from typing import Optional, Any
from sempy.fabric import FabricRestClient

from ...templates import DataPipelineTemplates
from ...sources.base import BaseSource
from .executor import LookupActivityExecutor
import json


class Lookup:
    """
    Builder class for creating lookup activity parameters for Microsoft Fabric Data Pipelines.

    This class enforces the use of prefixed parameter names (e.g., source_*) for clarity and consistency.
    Supports passing source parameters directly or as a list of dicts (items), as long as all required keys are present.

    Args:
        client (FabricRestClient): The Fabric REST client for API interactions.
        workspace (str): The name or ID of the Fabric workspace.
        pipeline (str | DataPipelineTemplates): The name or ID of the pipeline to execute, or a DataPipelineTemplates enum value.
        default_poll_timeout (int): Default timeout for polling the pipeline execution status.
        default_poll_interval (int): Default interval for polling the pipeline execution status.

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
        Sets the source for the lookup activity.
        Args:
            source (BaseSource): The source object (with source_*-prefixed params).
        Returns:
            Lookup: The builder instance.
        """
        self._source = source
        return self

    def params(self, **kwargs) -> "Lookup":
        """
        Sets additional parameters for the lookup activity.
        Args:
            **kwargs: Additional parameters to set.
        Returns:
            Lookup: The builder instance.
        """
        self._extra_params.update(kwargs)
        return self

    def items(self, items: list[dict]) -> "Lookup":
        """
        Sets additional parameters for the lookup activity using items.
        Args:
            items (list): A list of dicts, each containing all required source_* keys.
        Returns:
            Lookup: The builder instance.
        Raises:
            ValueError: If any item is missing required keys.
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
