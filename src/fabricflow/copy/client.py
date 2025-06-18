from fabricflow.pipeline.client import DataPipelineClient
from fabricflow.copy.utils import extract_copy_activity_info
import logging

logger = logging.getLogger(__name__)


class CopyActivityClient(DataPipelineClient):
    def __init__(
        self,
        client,
        workspace_id,
        pipeline_id,
        payload,
        default_poll_timeout=300,
        default_poll_interval=30,
    ):
        logger.info(
            "Initializing CopyActivityClient with workspace_id=%s, pipeline_id=%s",
            workspace_id,
            pipeline_id,
        )
        super().__init__(
            client,
            workspace_id,
            pipeline_id,
            payload,
            default_poll_timeout,
            default_poll_interval,
        )

    def run(self, query_activity_runs_filters=None):
        if query_activity_runs_filters is None:
            query_activity_runs_filters = []

        logger.info("Running pipeline with filters: %s", query_activity_runs_filters)
        pipeline_id, status, activity_results = super().run(
            query_activity_runs_filters
            or [{"operand": "ActivityType", "operator": "Equals", "values": ["Copy"]}],
        )

        logger.debug(
            "Pipeline run completed. pipeline_id=%s, status=%s, activity_results_count=%d",
            pipeline_id,
            status,
            len(activity_results) if activity_results else 0,
        )

        extracted_info = extract_copy_activity_info(activity_results)
        logger.info(
            "Extracted copy activity info for pipeline_id=%s (count=%d)",
            pipeline_id,
            len(extracted_info),
        )

        return pipeline_id, status, extracted_info
