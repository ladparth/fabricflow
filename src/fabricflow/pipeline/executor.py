"""
Microsoft Fabric Data Pipeline execution and monitoring.

This module provides classes and utilities for executing and monitoring
data pipelines in Microsoft Fabric. It handles pipeline triggering,
status polling, and result extraction.

Classes:
    DataPipelineExecutor: Main class for executing and monitoring data pipelines.
    PipelineStatus: Enum defining possible pipeline execution statuses.
    DataPipelineError: Custom exception for pipeline-related errors.

The module supports both synchronous and asynchronous pipeline execution
patterns with configurable timeout and polling intervals.
"""

from datetime import timedelta, datetime
import time
import logging
from logging import Logger
from typing import Optional, List, Dict, Any
from enum import Enum
from sempy.fabric import FabricRestClient
from ..core.workspaces.utils import get_workspace_id
from ..core.items.types import FabricItemType
from ..core.items.utils import resolve_item

logger: Logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Enumeration of possible Microsoft Fabric pipeline execution statuses.
    
    This enum provides type-safe constants for pipeline statuses, making code
    more readable and preventing typos when checking pipeline execution state.
    
    Attributes:
        COMPLETED: Pipeline execution finished successfully.
        FAILED: Pipeline execution failed with an error.
        CANCELLED: Pipeline execution was cancelled by user or system.
        RUNNING: Pipeline is currently executing.
        PENDING: Pipeline is queued for execution.
    """

    COMPLETED = "Completed"
    FAILED = "Failed" 
    CANCELLED = "Cancelled"
    RUNNING = "Running"
    PENDING = "Pending"


class DataPipelineError(Exception):
    """Custom exception for pipeline-related errors.
    
    This exception is raised when pipeline operations fail, such as:
    - Failed to trigger pipeline execution
    - Pipeline execution errors or timeouts
    - Invalid pipeline configurations
    - API communication errors during pipeline operations
    
    The exception typically wraps the underlying error while providing
    additional context about the pipeline operation that failed.
    """

    pass


class DataPipelineExecutor:
    """
    A client for managing Microsoft Fabric data pipeline executions.

    This class provides a high-level interface for executing and monitoring 
    data pipelines in Microsoft Fabric. It handles the complete pipeline
    execution lifecycle including triggering, status polling, and result
    extraction.

    Key capabilities:
    - Trigger pipeline execution with custom parameters
    - Poll for completion status with configurable timeouts
    - Query and filter activity run results
    - Handle pipeline errors and timeouts gracefully

    The executor automatically resolves workspace and pipeline names to IDs
    and provides detailed logging throughout the execution process.

    Attributes:
        client (FabricRestClient): Authenticated Fabric REST client.
        workspace_id (str): Resolved workspace ID.
        pipeline_id (str): Resolved pipeline ID.
        payload (Dict[str, Any]): Execution parameters payload.
        default_poll_timeout (int): Default timeout for polling operations.
        default_poll_interval (int): Default interval between status checks.

    Example:
        >>> from sempy.fabric import FabricRestClient
        >>> client = FabricRestClient()
        >>> executor = DataPipelineExecutor(
        ...     client=client,
        ...     workspace="my-workspace",
        ...     pipeline="my-pipeline", 
        ...     payload={"executionData": {"parameters": {}}}
        ... )
        >>> result = executor.run()
        >>> print(f"Pipeline status: {result['status']}")
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
        Initialize the DataPipelineExecutor.

        Args:
            client: The FabricRestClient instance for API calls
            workspace: The Fabric workspace name or ID
            pipeline: The pipeline name or ID to execute
            payload: The JSON payload to send when triggering the pipeline
            default_poll_timeout: How long to wait for operations (seconds)
            default_poll_interval: How often to check status (seconds)
        """
        self.client = client
        self.workspace_id = get_workspace_id(workspace)
        self.pipeline_id = resolve_item(
            pipeline,
            workspace=self.workspace_id,
            item_type=FabricItemType.DATA_PIPELINE,
        )
        self.payload = payload
        self.default_poll_timeout = default_poll_timeout
        self.default_poll_interval = default_poll_interval

        logger.info(
            f"DataPipelineExecutor initialized for workspace {self.workspace_id} and pipeline {self.pipeline_id}."
        )

    def trigger_pipeline(self) -> Optional[str]:
        """
        Trigger the pipeline execution.

        Returns:
            The job instance ID if successful, None if failed

        Raises:
            DataPipelineError: If the API call fails or response is invalid
        """
        logger.info(f"Triggering pipeline job for pipeline_id: {self.pipeline_id}...")

        try:
            response = self.client.post(
                f"v1/workspaces/{self.workspace_id}/items/{self.pipeline_id}/jobs/instances?jobType=Pipeline",
                json=self.payload,
            )
            response.raise_for_status()

            location = response.headers.get("Location")
            if not location:
                error_msg = f"Location header missing when triggering pipeline {self.pipeline_id}."
                logger.error(error_msg)
                raise DataPipelineError(error_msg)

            job_instance_id: str = str(location.split("/")[-1])

            logger.info(
                f"Pipeline triggered successfully. Job instance ID: {job_instance_id}"
            )
            return job_instance_id

        except Exception as e:
            error_msg: str = f"Error triggering pipeline {self.pipeline_id}: {e}"
            logger.error(error_msg)
            raise DataPipelineError(error_msg) from e

    def wait_for_visibility(self, job_instance_id: str) -> None:
        """
        Wait for the pipeline execution to become visible in the API.

        Sometimes there's a delay between triggering and the job being queryable.

        Args:
            job_instance_id: The job instance ID to check

        Raises:
            DataPipelineError: If timeout is reached
        """
        logger.info(
            f"Waiting for pipeline execution {job_instance_id} to be visible..."
        )

        # Give it an initial wait before starting to poll
        time.sleep(self.default_poll_interval)
        end_time: datetime = datetime.now() + timedelta(
            seconds=self.default_poll_timeout
        )

        while datetime.now() < end_time:
            try:
                response = self.client.get(
                    f"v1/workspaces/{self.workspace_id}/items/{self.pipeline_id}/jobs/instances/{job_instance_id}"
                )
                if response.status_code == 200:
                    logger.info(f"Pipeline execution {job_instance_id} is now visible.")
                    return

            except Exception as e:
                logger.warning(f"Error checking visibility: {e}")

            time.sleep(self.default_poll_interval)

        # If we reach here, we timed out waiting for visibility
        error_msg = f"Timeout waiting for pipeline execution {job_instance_id} to become visible"
        logger.error(error_msg)
        raise DataPipelineError(error_msg)

    def poll_for_status(self, job_instance_id: str) -> str:
        """
        Poll the pipeline execution until it reaches a final status.

        Args:
            job_instance_id: The job instance ID to monitor

        Returns:
            The final status (Completed, Failed, or Cancelled)

        Raises:
            DataPipelineError: If polling fails or timeout is reached
        """
        logger.info(f"Polling status for pipeline execution: {job_instance_id}...")

        end_time: datetime = datetime.now() + timedelta(
            seconds=self.default_poll_timeout
        )

        while datetime.now() < end_time:
            try:
                response = self.client.get(
                    f"v1/workspaces/{self.workspace_id}/items/{self.pipeline_id}/jobs/instances/{job_instance_id}"
                )
                response.raise_for_status()

                data = response.json()
                status = data.get("status")

                if not status:
                    logger.warning("Status field missing from response")
                    continue

                logger.info(f"Current status: {status}")

                # Check if we've reached a final status
                final_statuses: list[str] = [
                    PipelineStatus.COMPLETED.value,
                    PipelineStatus.FAILED.value,
                    PipelineStatus.CANCELLED.value,
                ]

                if status in final_statuses:
                    logger.info(f"Pipeline execution completed with status: {status}")
                    return status

            except Exception as e:
                logger.error(f"Error polling status: {e}")

            time.sleep(self.default_poll_interval)

        # If we get here, we timed out waiting for status
        error_msg = f"Timeout reached while polling status for job {job_instance_id}"
        logger.error(error_msg)
        raise DataPipelineError(error_msg)

    def query_activity_runs(
        self,
        job_instance_id: str,
        start_time: datetime,
        filters: Optional[List[Dict[str, Any]]] = None,
        timeout: int = 180,
    ) -> List[Dict[str, Any]]:
        """
        Query the activity runs for a pipeline execution.

        Args:
            job_instance_id: The job instance ID
            start_time: When the pipeline started (for filtering results)
            filters: Optional filters to apply to the query
            timeout: How long to wait for results

        Returns:
            List of activity run results
        """
        if filters is None:
            filters = []

        filter_params: dict[str, Any] = {
            "filters": filters,
            "orderBy": [{"orderBy": "ActivityRunStart", "order": "DESC"}],
            "lastUpdatedAfter": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "lastUpdatedBefore": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        activity_results: List[Dict[str, Any]] = []
        poll_interval = 30
        end_time: datetime = datetime.now() + timedelta(seconds=timeout)

        while not activity_results and datetime.now() < end_time:
            try:
                response = self.client.post(
                    f"v1/workspaces/{self.workspace_id}/datapipelines/pipelineruns/{job_instance_id}/queryactivityruns",
                    json=filter_params,
                )
                response.raise_for_status()
                activity_results = response.json()

                if activity_results:
                    logger.info(f"Found {len(activity_results)} activity run results")
                    break

            except Exception as e:
                logger.warning(f"Error querying activity runs: {e}")

            if not activity_results:
                logger.info("No activity runs found yet, waiting...")
                time.sleep(poll_interval)
                # Update the end time filter for the next query
                filter_params["lastUpdatedBefore"] = datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

        if not activity_results:
            logger.warning(
                f"No activity runs found for job {job_instance_id} within timeout period"
            )

        return activity_results

    def run(
        self, query_activity_runs_filters: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete pipeline workflow.

        This is the main method that:
        1. Triggers the pipeline
        2. Waits for it to be visible
        3. Polls for completion
        4. Queries activity runs

        Args:
            query_activity_runs_filters: Optional filters for activity run queries

        Returns:
            Dict with keys: pipeline_id, status, activity_results

        Raises:
            DataPipelineError: If any step in the process fails
        """
        if query_activity_runs_filters is None:
            query_activity_runs_filters = []

        start_time: datetime = datetime.now()
        logger.info(
            f"Starting pipeline execution workflow for pipeline {self.pipeline_id}"
        )

        try:
            # Step 1: Trigger the pipeline
            job_instance_id: str | None = self.trigger_pipeline()

            if job_instance_id is None:
                raise DataPipelineError(
                    "Failed to trigger pipeline: job_instance_id is None"
                )

            # Step 2: Wait for visibility
            self.wait_for_visibility(job_instance_id)

            # Step 3: Poll for completion
            final_status: str = self.poll_for_status(job_instance_id)

            # Step 4: Get activity runs
            activity_results: list[dict[str, Any]] = self.query_activity_runs(
                job_instance_id, start_time, query_activity_runs_filters
            )

            logger.info(
                f"Pipeline workflow completed. Status: {final_status}, Activities: {len(activity_results)}"
            )
            # Return the results
            return {
                "pipeline_id": self.pipeline_id,
                "status": final_status,
                "activity_results": activity_results,
            }

        except DataPipelineError:
            raise
        except Exception as e:
            error_msg: str = f"Unexpected error in pipeline workflow: {e}"
            logger.error(error_msg)
            raise DataPipelineError(error_msg) from e
