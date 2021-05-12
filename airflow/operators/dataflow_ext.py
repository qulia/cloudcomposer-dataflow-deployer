from typing import Any, Dict, Optional, Sequence, Union

from airflow.models import BaseOperator
from airflow.providers.google.cloud.hooks.dataflow import (
    DEFAULT_DATAFLOW_LOCATION,
    DataflowHook,
    process_line_and_extract_dataflow_job_id_callback,
)
from airflow.utils.decorators import apply_defaults


class DataflowTemplatedJobStopOperator(BaseOperator):
    template_fields = [
        "job_name",
        "location",
        "project_id",
        "gcp_conn_id",
    ]
    ui_color = "#F7D57A"

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
            self.log.info(f"not found")
        return

    def on_kill(self) -> None:
        self.log.info("On kill.")


# Current implementation does not pass append_job_name to the hook method
# https://github.com/apache/airflow/blob/master/airflow/providers/google/cloud/operators/dataflow.py#L691
class DataflowTemplatedJobStartOperator2(BaseOperator):
    template_fields = [
        "template",
        "job_name",
        "options",
        "parameters",
        "project_id",
        "location",
        "gcp_conn_id",
        "impersonation_chain",
        "environment",
    ]
    ui_color = "#CBFCD3"

    @apply_defaults
    def __init__(  # pylint: disable=too-many-arguments
            self,
            *,
            template: str,
            job_name: str = "{{task.task_id}}",
            options: Optional[Dict[str, Any]] = None,
            dataflow_default_options: Optional[Dict[str, Any]] = None,
            parameters: Optional[Dict[str, str]] = None,
            project_id: Optional[str] = None,
            append_job_name: bool = True,
            location: str = DEFAULT_DATAFLOW_LOCATION,
            gcp_conn_id: str = "google_cloud_default",
            delegate_to: Optional[str] = None,
            poll_sleep: int = 10,
            impersonation_chain: Optional[Union[str, Sequence[str]]] = None,
            drain_pipeline: bool = False,
            environment: Optional[Dict] = None,
            cancel_timeout: Optional[int] = 10 * 60,
            wait_until_finished: Optional[bool] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.template = template
        self.job_name = job_name
        self.options = options or {}
        self.dataflow_default_options = dataflow_default_options or {}
        self.parameters = parameters or {}
        self.project_id = project_id
        self.append_job_name = append_job_name
        self.location = location
        self.gcp_conn_id = gcp_conn_id
        self.delegate_to = delegate_to
        self.poll_sleep = poll_sleep
        self.job_id = None
        self.hook: Optional[DataflowHook] = None
        self.impersonation_chain = impersonation_chain
        self.drain_pipeline = drain_pipeline
        self.environment = environment
        self.cancel_timeout = cancel_timeout
        self.wait_until_finished = wait_until_finished

    def execute(self, context) -> dict:
        self.hook = DataflowHook(
            gcp_conn_id=self.gcp_conn_id,
            delegate_to=self.delegate_to,
            poll_sleep=self.poll_sleep,
            impersonation_chain=self.impersonation_chain,
            drain_pipeline = self.drain_pipeline,
            cancel_timeout=self.cancel_timeout,
            wait_until_finished=self.wait_until_finished,
        )

        def set_current_job_id(job_id):
            self.job_id = job_id

        options = self.dataflow_default_options
        options.update(self.options)
        job = self.hook.start_template_dataflow(
            job_name=self.job_name,
            variables=options,
            parameters=self.parameters,
            dataflow_template=self.template,
            on_new_job_id_callback=set_current_job_id,
            project_id=self.project_id,
            append_job_name=self.append_job_name,
            location=self.location,
            environment=self.environment,
        )

        return job

    def on_kill(self) -> None:
        self.log.info("On kill.")
        if self.job_id:
            self.hook.cancel_job(job_id=self.job_id, project_id=self.project_id)
