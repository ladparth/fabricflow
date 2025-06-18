from datetime import timedelta, datetime
import time
import logging

logger = logging.getLogger(__name__)


class DataPipelineClient:
    def __init__(
        self,
        client,
        workspace_id,
        pipeline_id,
        payload,
        default_poll_timeout=300,
        default_poll_interval=30,
    ):
        self.client = client
        self.workspace_id = workspace_id
        self.pipeline_id = pipeline_id
        self.payload = payload
        self.default_poll_timeout = default_poll_timeout
        self.default_poll_interval = default_poll_interval
        logger.info(
            f"DataPipelineClient initialized for workspace {workspace_id} and pipeline {pipeline_id}."
        )

    def trigger_pipeline(self):
        logger.info(f"Triggering pipeline job for pipeline_id: {self.pipeline_id}...")
        try:
            response = self.client.post(
                f"v1/workspaces/{self.workspace_id}/items/{self.pipeline_id}/jobs/instances?jobType=Pipeline",
                json=self.payload,
            )
            response.raise_for_status()
            location = response.headers.get("Location")
            if not location:
                logger.error(
                    f"Location header missing when triggering pipeline {self.pipeline_id}."
                )
                return None
            return str(location.split("/")[-1])
        except Exception as e:
            logger.error(f"Error triggering pipeline {self.pipeline_id}: {e}")
            return None

    def wait_for_visibility(self, job_instance_id):
        logger.info(
            f"Waiting for pipeline execution {job_instance_id} to be visible..."
        )
        time.sleep(self.default_poll_interval)
        end_time = datetime.now() + timedelta(seconds=self.default_poll_timeout)

        while datetime.now() < end_time:
            try:
                status_code = self.client.get(
                    f"v1/workspaces/{self.workspace_id}/items/{self.pipeline_id}/jobs/instances/{job_instance_id}"
                ).status_code
                if status_code == 200:
                    logger.info(f"Pipeline execution {job_instance_id} is now visible.")
                    break
            except Exception as e:
                logger.warning(f"Error checking visibility: {e}")
            time.sleep(self.default_poll_interval)

    def poll_for_status(self, job_instance_id):
        logger.info(f"Polling status for pipeline execution: {job_instance_id}...")
        while True:
            try:
                resp = self.client.get(
                    f"v1/workspaces/{self.workspace_id}/items/{self.pipeline_id}/jobs/instances/{job_instance_id}"
                )
                resp.raise_for_status()
                status = resp.json().get("status")
                logger.info(f"Status: {status}")
                if status in ["Completed", "Failed", "Cancelled"]:
                    return status
            except Exception as e:
                logger.error(f"Error polling status: {e}")
                return "Failed"
            time.sleep(self.default_poll_interval)

    def query_activity_runs(
        self, job_instance_id, start_time, filters=None, timeout=180
    ):
        if filters is None:
            filters = []
        filter_params = {
            "filters": filters,
            "orderBy": [{"orderBy": "ActivityRunStart", "order": "DESC"}],
            "lastUpdatedAfter": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "lastUpdatedBefore": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        activity_results = []
        poll_interval = 30
        end_time = datetime.now() + timedelta(seconds=timeout)
        while not activity_results and datetime.now() < end_time:
            try:
                resp = self.client.post(
                    f"v1/workspaces/{self.workspace_id}/datapipelines/pipelineruns/{job_instance_id}/queryactivityruns",
                    json=filter_params,
                )
                resp.raise_for_status()
                activity_results = resp.json()
            except Exception as e:
                logger.warning(f"Error querying activity runs: {e}")
                activity_results = []
            if not activity_results:
                time.sleep(poll_interval)
                filter_params["lastUpdatedBefore"] = datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )
        if not activity_results:
            logger.error(
                f"Timeout reached while querying activity runs for job {job_instance_id}"
            )
        return activity_results

    def run(self, query_activity_runs_filters=None):
        if query_activity_runs_filters is None:
            query_activity_runs_filters = []
        start_time = datetime.now()

        logger.info(f"Attempting to trigger pipeline {self.pipeline_id}.")
        job_instance_id = self.trigger_pipeline()

        if not job_instance_id:
            logger.error(
                f"[{datetime.now()}] Failed to trigger pipeline {self.pipeline_id}."
            )
            return self.pipeline_id, "Failed", []

        self.wait_for_visibility(job_instance_id)

        status = self.poll_for_status(job_instance_id)

        logger.info(f"Pipeline {self.pipeline_id} status: {status}")

        activity_results = self.query_activity_runs(
            job_instance_id, start_time, query_activity_runs_filters
        )
        if not activity_results:
            logger.warning(
                f"No activity runs found for pipeline {self.pipeline_id} with job instance {job_instance_id}."
            )

        return self.pipeline_id, status, activity_results
