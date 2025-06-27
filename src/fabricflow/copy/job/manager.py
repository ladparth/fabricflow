from typing import Optional, Any
from sempy.fabric import FabricRestClient
from .base import BaseSource, BaseSink
from ..executor import CopyActivityExecutor
import json


class CopyManager:
    """
    Builder class for creating copy activity parameters for Microsoft Fabric Data Pipelines.

    This class enforces the use of prefixed parameter names (e.g., source_*, sink_*) for clarity and consistency.
    Supports passing source and sink parameters directly or as a list of dicts (items), as long as all required keys are present.
    """

    def __init__(
        self,
        client: FabricRestClient,
        workspace: str,
        pipeline: str,
        default_poll_timeout: int = 300,
        default_poll_interval: int = 15,
    ) -> None:
        self.workspace = workspace
        self.pipeline = pipeline
        self.client = client
        self._source: Optional[BaseSource] = None
        self._sink: Optional[BaseSink] = None
        self._extra_params: dict = {}
        self._payload = {"executionData": {"parameters": {}}}
        self.default_poll_timeout = default_poll_timeout
        self.default_poll_interval = default_poll_interval

    def source(self, source: BaseSource) -> "CopyManager":
        """
        Sets the source for the copy activity.
        Args:
            source (BaseSource): The source object (with source_*-prefixed params).
        Returns:
            CopyManager: The builder instance.
        """
        self._source = source
        return self

    def sink(self, sink: BaseSink) -> "CopyManager":
        """
        Sets the sink for the copy activity.
        Args:
            sink (BaseSink): The sink object (with sink_*-prefixed params).
        Returns:
            CopyManager: The builder instance.
        """
        self._sink = sink
        return self

    def params(self, **kwargs) -> "CopyManager":
        """
        Sets additional parameters for the copy activity.
        Args:
            **kwargs: Additional parameters to set.
        Returns:
            CopyManager: The builder instance.
        """
        self._extra_params.update(kwargs)
        return self

    def items(self, items: list[dict]) -> "CopyManager":
        """
        Sets additional parameters for the copy activity using items.
        Args:
            items (list): A list of dicts, each containing all required source_*/sink_* keys.
        Returns:
            CopyManager: The builder instance.
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

        self._extra_params["items"] = items
        return self

    def build(self) -> "CopyManager":
        """
        Builds the copy activity parameters.
        Returns:
            CopyManager: The builder instance with payload ready for execution.
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
        Converts the CopyManager object to a dictionary representation.
        This includes the workspace, pipeline, source, sink, and extra parameters.

        Returns:
            dict: Dictionary representation of the CopyManager object.
        """
        return {
            "workspace": self.workspace,
            "pipeline": self.pipeline,
            "payload": self._payload,
        }

    def __str__(self) -> str:
        """

        Returns a JSON string representation of the CopyManager object.
        This includes the workspace, pipeline, source, sink, and extra parameters.

        """

        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self) -> str:
        """
        Returns a string representation of the CopyManager object.
        """
        return self.__str__()
