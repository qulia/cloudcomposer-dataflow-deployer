from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators import PythonOperator
from airflow.models import Variable
from typing import Callable, Dict, List
from operators.dataflow_ext import (
    DataflowTemplatedJobStopOperator,
    DataflowTemplatedJobStartOperator2
)

from airflow.providers.google.cloud.sensors.dataflow import (
    DataflowJobAutoScalingEventsSensor,
    DataflowJobMessagesSensor,
    DataflowJobMetricsSensor,
)

from airflow.exceptions import AirflowException

with models.DAG(
    "gcp_dataflow_template_deployer",
    start_date=days_ago(1),
    schedule_interval=None
) as dag_template:
    # Print the received dag_run configuration.
    # The DAG run configuration contains information about the
    # Cloud Storage object change.
    print_content = BashOperator(
        task_id='print_gcs_info',
        bash_command="echo Triggered from GCF: {{ dag_run.conf }}",
        dag=dag_template)

    stop_job = DataflowTemplatedJobStopOperator(
        task_id="stop-template-job",
        job_name="{{ dag_run.conf['rollout']['from']['job_name'] }}",
        project_id="{{ dag_run.conf['rollout']['from']['project_id'] }}",
        location="{{ dag_run.conf['rollout']['from']['location'] }}",
        drain_pipeline=False,
    )

    def run_start_operator(**kwargs):
        job_name = kwargs['dag_run'].conf['rollout']['to']['job_name']
        template = kwargs['dag_run'].conf['rollout']['to']['template']
        location = kwargs['dag_run'].conf['rollout']['to']['location']
        environment = kwargs['dag_run'].conf['rollout']['to']['environment']
        parameters = kwargs['dag_run'].conf['rollout']['to']['parameters']
        # https://github.com/apache/airflow/blob/0f327788b5b0887c463cb83dd8f732245da96577/airflow/providers/google/cloud/hooks/dataflow.py#L618
        start_job_task = DataflowTemplatedJobStartOperator2(
            task_id="start-template-job",
            job_name=job_name,
            append_job_name=False,
            template=template,
            # https://cloud.google.com/dataflow/docs/reference/rest/v1b3/RuntimeEnvironment
            environment=environment,
            parameters=parameters,
            location=location,
        )
        return start_job_task.execute({})

    start_job = PythonOperator(
        task_id='start-template-job-call',
        python_callable=run_start_operator,
        dag=dag_template,
        provide_context=True)

    # https://github.com/apache/airflow/blob/master/airflow/providers/google/cloud/example_dags/example_dataflow.py
    # [START howto_sensor_wait_for_job_metric]
    def check_metric_scalar_gte(metric_name: str, value: int) -> Callable:
        """Check is metric greater than equals to given value."""

        def callback(metrics: List[Dict]) -> bool:
            dag_template.log.info("Looking for '%s' >= %d", metric_name, value)
            for metric in metrics:
                context = metric.get("name", {}).get("context", {})
                original_name = context.get("original_name", "")
                tentative = context.get("tentative", "")
                if original_name == "Service-cpu_num_seconds" and not tentative:
                    return metric["scalar"] >= value
            raise AirflowException(f"Metric '{metric_name}' not found in metrics")

        return callback

    wait_for_job_metric = DataflowJobMetricsSensor(
        task_id="wait-for-job-metric",
        job_id="{{task_instance.xcom_pull('start-template-job-call')['id']}}",
        location="{{ dag_run.conf['rollout']['to']['location'] }}",
        callback=check_metric_scalar_gte(metric_name="Service-cpu_num_seconds", value=100),
    )
    # [END howto_sensor_wait_for_job_metric]

    # [START howto_sensor_wait_for_job_message]
    def check_message(messages: List[dict]) -> bool:
        """Check message"""
        for message in messages:
            if "Adding workflow start and stop steps." in message.get("messageText", ""):
                return True
        return False

    wait_for_job_message = DataflowJobMessagesSensor(
        task_id="wait-for-job-message",
        job_id="{{task_instance.xcom_pull('start-template-job-call')['id']}}",
        location="{{ dag_run.conf['rollout']['to']['location'] }}",
        callback=check_message,
    )
    # [END howto_sensor_wait_for_job_message]

    # [START howto_sensor_wait_for_job_autoscaling_event]
    def check_autoscaling_event(autoscaling_events: List[dict]) -> bool:
        """Check autoscaling event"""
        for autoscaling_event in autoscaling_events:
            if "Worker pool started." in autoscaling_event.get("description", {}).get("messageText", ""):
                return True
        return False

    wait_for_job_autoscaling_event = DataflowJobAutoScalingEventsSensor(
        task_id="wait-for-job-autoscaling-event",
        job_id="{{task_instance.xcom_pull('start-template-job-call')['id']}}",
        location="{{ dag_run.conf['rollout']['to']['location'] }}",
        callback=check_autoscaling_event,
    )
    # [END howto_sensor_wait_for_job_autoscaling_event]

    print_content >> stop_job
    stop_job >> start_job
    start_job >> wait_for_job_metric
    start_job >> wait_for_job_message
    start_job >> wait_for_job_autoscaling_event
