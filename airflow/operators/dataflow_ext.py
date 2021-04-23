from typing import Any, Dict, Optional, Sequence, Union

from airflow.models import BaseOperator
from airflow.providers.google.cloud.hooks.dataflow import (
    DEFAULT_DATAFLOW_LOCATION,
    DataflowHook,
    process_line_and_extract_dataflow_job_id_callback,
)
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowTaskTimeout
import json

class DataflowTemplatedJobStopOperator(BaseOperator):
    template_fields = [
        "job_name",
        "location",
        "project_id",
        "gcp_conn_id",
    ]

    @apply_defaults
    def __init__(  # pylint: disable=too-many-arguments
            self,
            *,
            project_id: str,
            job_name: str = "{{task.task_id}}",
            location: str = DEFAULT_DATAFLOW_LOCATION,
            gcp_conn_id: str = "google_cloud_default",
            delegate_to: Optional[str] = None,
            poll_sleep: int = 10,
            impersonation_chain: Optional[Union[str, Sequence[str]]] = None,
            drain_pipeline: bool = False,
            cancel_timeout: Optional[int] = 10 * 60,
            wait_until_finished: Optional[bool] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.job_name = job_name
        self.project_id = project_id
        self.location = location
        self.gcp_conn_id = gcp_conn_id
        self.delegate_to = delegate_to
        self.poll_sleep = poll_sleep
        self.job_id = None
        self.hook: Optional[DataflowHook] = None
        self.impersonation_chain = impersonation_chain
        self.cancel_timeout = cancel_timeout
        self.drain_pipeline = drain_pipeline
        self.wait_until_finished = wait_until_finished

    def execute(self, context) -> dict:
        self.hook = DataflowHook(
            gcp_conn_id=self.gcp_conn_id,
            delegate_to=self.delegate_to,
            poll_sleep=self.poll_sleep,
            impersonation_chain=self.impersonation_chain,
            drain_pipeline=self.drain_pipeline,
            cancel_timeout=self.cancel_timeout,
            wait_until_finished=self.wait_until_finished,
        )

        try:
            self.hook.cancel_job(
                job_name=self.job_name,
                project_id=self.project_id,
                location=self.location,
            )
        except ValueError:
            self.log.info(f"timeout {self.location}")
        return

    def on_kill(self) -> None:
        self.log.info("On kill.")
        if self.job_id:
            self.hook.cancel_job(job_id=self.job_id, project_id=self.project_id)