from typing import Optional, List, Dict, Any
import logging
from logging import Logger
from ...executor import DataPipelineExecutor, DataPipelineError
from sempy.fabric import FabricRestClient

logger: Logger = logging.getLogger(__name__)


class LookupActivityExecutor(DataPipelineExecutor):
    """
    Specialized client for pipelines that contain lookup activities.

    This class extends DataPipelineExecutor to:
    - Automatically filter for lookup activities
    - Extract and process lookup activity information
    - Provide lookup-specific functionality
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
        Initialize the LookupActivityExecutor.

        Args:
            client: The FabricRestClient instance for API calls
            workspace: The Fabric workspace name or ID
            pipeline: The pipeline name or ID to execute
            payload: The JSON payload to send when triggering the pipeline
            default_poll_timeout: How long to wait for operations (seconds)
            default_poll_interval: How often to check status (seconds)
        """

        logger.info(
            "Initializing LookupActivityExecutor with workspace=%s, pipeline=%s",
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
            f"LookupActivityExecutor initialized for workspace {self.workspace_id} and pipeline {self.pipeline_id}."
        )

    def get_lookup_activity_filter(self) -> List[Dict[str, Any]]:
        """
        Get the default filter for lookup activities.

        Returns:
            List containing the lookup activity filter
        """
        return [{"operand": "ActivityType", "operator": "Equals", "values": ["Lookup"]}]

    def run(
        self, query_activity_runs_filters: Optional[List[Dict[str, Any]]] = None
    ) -> dict[str, Any]:
        """
        Execute the pipeline workflow specifically for lookup activities.

        This method:
        1. Runs the base pipeline workflow
        2. Automatically filters for lookup activities (if no filters provided)
        3. Extracts lookup-specific information from the results

        Args:
            query_activity_runs_filters: Optional filters for activity run queries.
                                         If None, defaults to lookup activity filter.

        Returns:
            dict containing pipeline_id, final_status, and extracted_lookup_info

        Raises:
            DataPipelineError: If the pipeline execution or lookup extraction fails
        """
        logger.info(
            "Running lookup activity pipeline with filters: %s",
            query_activity_runs_filters,
        )

        try:
            # Use lookup activity filter if no filters provided
            if query_activity_runs_filters is None:
                query_activity_runs_filters = self.get_lookup_activity_filter()
                logger.info("Using default lookup activity filter")

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
            error_msg: str = f"Error in lookup activity pipeline workflow: {e}"
            logger.error(error_msg)
            if isinstance(e, DataPipelineError):
                raise
            else:
                raise DataPipelineError(error_msg) from e
