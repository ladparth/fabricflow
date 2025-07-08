"""
Base classes and abstractions for Microsoft Fabric data pipeline activities.

This module provides the foundational abstract base class for all activity-specific
pipeline executors in Microsoft Fabric. Activity executors handle the execution
and monitoring of specific activity types within data pipelines, such as Copy
activities, Lookup activities, and other data processing operations.

Classes:
    BaseActivityExecutor: Abstract base class for activity-specific pipeline executors.

The BaseActivityExecutor extends the core DataPipelineExecutor with activity-specific
functionality, including automatic filtering for specific activity types, standardized
result processing, and extensible hooks for activity-specific customizations.

Key Features:
- Activity-type filtering for targeted result extraction
- Standardized execution workflow for all activity types
- Extensible design with processing hooks for subclasses
- Comprehensive error handling and logging
- Type-safe interface with proper abstractions

Activity Execution Workflow:
1. Initialize executor with activity-specific configuration
2. Execute pipeline with automatic activity type filtering
3. Process activity-specific results through hooks
4. Return standardized result format with execution details

Example:
    ```python
    # Subclass implementation for Copy activities
    class CopyActivityExecutor(BaseActivityExecutor):
        def get_activity_type(self) -> str:
            return "Copy"

        def process_activity_results(self, result: dict[str, Any]) -> dict[str, Any]:
            # Copy-specific result processing
            if "activity_results" in result:
                for activity in result["activity_results"]:
                    if activity.get("activityType") == "Copy":
                        # Process copy-specific metrics
                        activity["processed"] = True
            return result

    # Usage
    executor = CopyActivityExecutor(
        client=fabric_client,
        workspace="MyWorkspace",
        pipeline="CopyPipeline",
        payload=copy_payload
    )

    result = executor.run()
    print(f"Copy activity completed: {result['status']}")
    ```

Architecture Benefits:
- Consistent interface across all activity types
- Automatic activity filtering reduces result noise
- Extensible design supports new activity types
- Comprehensive logging for debugging and monitoring
- Error handling with proper exception chaining

Dependencies:
- sempy.fabric: For FabricRestClient integration
- fabricflow.pipeline.executor: For base DataPipelineExecutor functionality

Note:
    This is an abstract base class and cannot be instantiated directly.
    Concrete implementations must implement the get_activity_type() method
    and optionally override process_activity_results() for custom processing.
"""

from typing import Optional, List, Dict, Any
import logging
from logging import Logger
from abc import ABC, abstractmethod
from ..executor import DataPipelineExecutor, DataPipelineError
from sempy.fabric import FabricRestClient

logger: Logger = logging.getLogger(__name__)


class BaseActivityExecutor(DataPipelineExecutor, ABC):
    """
    Abstract base class for activity-specific pipeline executors in Microsoft Fabric.

    This class extends DataPipelineExecutor to provide specialized functionality for
    executing and monitoring specific types of activities within data pipelines.
    It automatically handles activity type filtering, standardizes the execution
    workflow, and provides hooks for activity-specific result processing.

    The BaseActivityExecutor serves as the foundation for all concrete activity
    executors (Copy, Lookup, etc.), ensuring consistent behavior and interfaces
    across different activity types while allowing for specialized customization.

    Key Features:
    - Automatic activity type filtering for targeted result extraction
    - Standardized execution workflow with error handling
    - Extensible design with processing hooks for subclasses
    - Comprehensive logging throughout the execution lifecycle
    - Type-safe interface with proper abstractions

    Workflow:
    1. Initialize with activity-specific configuration and payload
    2. Execute pipeline with automatic activity filtering applied
    3. Process results through activity-specific hooks if overridden
    4. Return standardized result format with execution details

    Attributes:
        Inherits all attributes from DataPipelineExecutor including:
        - client: FabricRestClient for API interactions
        - workspace_id: Resolved workspace identifier
        - pipeline_id: Resolved pipeline identifier
        - payload: Execution payload with parameters
        - default_poll_timeout: Timeout for polling operations
        - default_poll_interval: Interval between status checks

    Abstract Methods:
        get_activity_type(): Must return the activity type name for filtering.

    Virtual Methods:
        process_activity_results(): Override for activity-specific result processing.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client for API interactions.
        workspace (str): Name or ID of the target Fabric workspace.
        pipeline (str): Name or ID of the pipeline to execute.
        payload (Dict[str, Any]): JSON payload containing execution parameters.
        default_poll_timeout (int): Default timeout in seconds for polling operations.
                                   Defaults to 300 seconds (5 minutes).
        default_poll_interval (int): Default interval in seconds between status checks.
                                    Defaults to 15 seconds.

    Raises:
        TypeError: If client is not a FabricRestClient instance.
        ValueError: If workspace or pipeline cannot be resolved.
        DataPipelineError: If pipeline execution fails.

    Example:
        ```python
        # Concrete implementation
        class CopyActivityExecutor(BaseActivityExecutor):
            def get_activity_type(self) -> str:
                return "Copy"

            def process_activity_results(self, result: dict[str, Any]) -> dict[str, Any]:
                # Add copy-specific processing
                copy_activities = [
                    activity for activity in result.get("activity_results", [])
                    if activity.get("activityType") == "Copy"
                ]
                result["copy_activity_count"] = len(copy_activities)
                return result

        # Usage
        copy_executor = CopyActivityExecutor(
            client=fabric_client,
            workspace="analytics-workspace",
            pipeline="copy-pipeline",
            payload={
                "executionData": {
                    "parameters": {
                        "source_query": "SELECT * FROM customers",
                        "sink_table_name": "customer_data"
                    }
                }
            }
        )

        result = copy_executor.run()
        print(f"Execution status: {result['status']}")
        print(f"Copy activities: {result.get('copy_activity_count', 0)}")
        ```

    Note:
        This is an abstract base class that cannot be instantiated directly.
        Subclasses must implement get_activity_type() and optionally override
        process_activity_results() for specialized behavior.
    """

    def __init__(
        self,
        client: FabricRestClient,
        workspace: str,
        pipeline: str,
        payload: Dict[str, Any],
        default_poll_timeout: int = 300,
        default_poll_interval: int = 15,
    ) -> None:
        """
        Initialize the BaseActivityExecutor.

        Args:
            client: The FabricRestClient instance for API calls
            workspace: The Fabric workspace name or ID
            pipeline: The pipeline name or ID to execute
            payload: The JSON payload to send when triggering the pipeline
            default_poll_timeout: How long to wait for operations (seconds)
            default_poll_interval: How often to check status (seconds)
        """
        activity_type = self.get_activity_type()
        logger.info(
            "Initializing %sActivityExecutor with workspace=%s, pipeline=%s",
            activity_type,
            workspace,
            pipeline,
        )

        super().__init__(
            client=client,
            workspace=workspace,
            pipeline=pipeline,
            payload=payload,
            default_poll_timeout=default_poll_timeout,
            default_poll_interval=default_poll_interval,
        )

        logger.info(
            f"{activity_type}ActivityExecutor initialized for workspace {self.workspace_id} and pipeline {self.pipeline_id}."
        )

    @abstractmethod
    def get_activity_type(self) -> str:
        """
        Get the activity type name for this executor.

        Returns:
            The activity type name (e.g., "Copy", "Lookup")
        """
        pass

    def get_activity_filter(self) -> List[Dict[str, Any]]:
        """
        Get the default filter for this activity type.

        Returns:
            List containing the activity filter
        """
        activity_type = self.get_activity_type()
        return [
            {"operand": "ActivityType", "operator": "Equals", "values": [activity_type]}
        ]

    def run(
        self, query_activity_runs_filters: Optional[List[Dict[str, Any]]] = None
    ) -> dict[str, Any]:
        """
        Execute the pipeline workflow for this specific activity type.

        This method:
        1. Runs the base pipeline workflow
        2. Automatically filters for the specific activity type (if no filters provided)
        3. Allows for activity-specific processing via hooks

        Args:
            query_activity_runs_filters: Optional filters for activity run queries.
                                       If None, defaults to activity type filter.

        Returns:
            dict containing pipeline_id, final_status, and activity results

        Raises:
            DataPipelineError: If the pipeline execution fails
        """
        activity_type = self.get_activity_type()
        logger.info(
            "Running %s activity pipeline with filters: %s",
            activity_type.lower(),
            query_activity_runs_filters,
        )

        try:
            # Use activity type filter if no filters provided
            if query_activity_runs_filters is None:
                query_activity_runs_filters = self.get_activity_filter()
                logger.info("Using default %s activity filter", activity_type.lower())

            # Run the base pipeline workflow
            result: dict[str, Any] = super().run(query_activity_runs_filters)

            # Allow subclasses to process results
            result = self.process_activity_results(result)

            logger.debug(
                "Pipeline run completed. pipeline_id=%s, status=%s, activity_results_count=%d",
                result.get("pipeline_id"),
                result.get("status"),
                len(result.get("activity_results", [])),
            )

            return result

        except Exception as e:
            error_msg: str = (
                f"Error in {activity_type.lower()} activity pipeline workflow: {e}"
            )
            logger.error(error_msg)
            if isinstance(e, DataPipelineError):
                raise
            else:
                raise DataPipelineError(error_msg) from e

    def process_activity_results(self, result: dict[str, Any]) -> dict[str, Any]:
        """
        Hook for subclasses to process activity-specific results.

        Args:
            result: The result dictionary from the pipeline execution

        Returns:
            The processed result dictionary
        """
        # Default implementation - no processing
        return result
