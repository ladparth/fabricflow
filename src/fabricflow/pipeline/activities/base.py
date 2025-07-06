from typing import Optional, List, Dict, Any
import logging
from logging import Logger
from abc import ABC, abstractmethod
from ..executor import DataPipelineExecutor, DataPipelineError
from sempy.fabric import FabricRestClient

logger: Logger = logging.getLogger(__name__)


class BaseActivityExecutor(DataPipelineExecutor, ABC):
    """
    Base class for activity-specific pipeline executors.

    This class provides common functionality for activity-specific executors:
    - Automatic filtering for specific activity types
    - Template for activity-specific workflow execution
    - Extensible design for future customizations
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
