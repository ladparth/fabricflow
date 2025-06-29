from typing import Optional, List, Dict, Any
import logging
from logging import Logger
from ..pipeline.executor import DataPipelineExecutor, DataPipelineError
from sempy.fabric import FabricRestClient

logger: Logger = logging.getLogger(__name__)


class CopyActivityExecutor(DataPipelineExecutor):
    """
    Specialized client for pipelines that contain copy activities.

    This class extends DataPipelineExecutor to:
    - Automatically filter for copy activities
    - Extract and process copy activity information
    - Provide copy-specific functionality
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
        Initialize the CopyActivityExecutor.

        Args:
            client: The FabricRestClient instance for API calls
            workspace: The Fabric workspace name or ID
            pipeline: The pipeline name or ID to execute
            payload: The JSON payload to send when triggering the pipeline
            default_poll_timeout: How long to wait for operations (seconds)
            default_poll_interval: How often to check status (seconds)
        """

        logger.info(
            "Initializing CopyActivityExecutor with workspace=%s, pipeline=%s",
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
            f"CopyActivityExecutor initialized for workspace {self.workspace_id} and pipeline {self.pipeline_id}."
        )

    def get_copy_activity_filter(self) -> List[Dict[str, Any]]:
        """
        Get the default filter for copy activities.

        Returns:
            List containing the copy activity filter
        """
        return [{"operand": "ActivityType", "operator": "Equals", "values": ["Copy"]}]

    def run(
        self, query_activity_runs_filters: Optional[List[Dict[str, Any]]] = None
    ) -> dict[str, Any]:
        """
        Execute the pipeline workflow specifically for copy activities.

        This method:
        1. Runs the base pipeline workflow
        2. Automatically filters for copy activities (if no filters provided)
        3. Extracts copy-specific information from the results

        Args:
            query_activity_runs_filters: Optional filters for activity run queries.
                                       If None, defaults to copy activity filter.

        Returns:
            dict containing pipeline_id, final_status, and extracted_copy_info

        Raises:
            DataPipelineError: If the pipeline execution or copy extraction fails
        """
        logger.info(
            "Running copy activity pipeline with filters: %s",
            query_activity_runs_filters,
        )

        try:
            # Use copy activity filter if no filters provided
            if query_activity_runs_filters is None:
                query_activity_runs_filters = self.get_copy_activity_filter()
                logger.info("Using default copy activity filter")

            # Run the base pipeline workflow
            result: dict[str, Any] = super().run(query_activity_runs_filters)

            logger.debug(
                "Pipeline run completed. pipeline_id=%s, status=%s, activity_results_count=%d",
                result.get("pipeline_id"),
                result.get("status"),
                len(result.get("activity_results", [])),
            )

            return result

        except Exception as e:
            error_msg: str = f"Error in copy activity pipeline workflow: {e}"
            logger.error(error_msg)
            if isinstance(e, DataPipelineError):
                raise
            else:
                raise DataPipelineError(error_msg) from e
