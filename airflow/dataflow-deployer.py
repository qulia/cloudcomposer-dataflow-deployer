from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators import PythonOperator
from airflow.models import Variable

from operators.dataflow_ext import (
    DataflowTemplatedJobStopOperator
)

from airflow.providers.google.cloud.operators.dataflow import (
    CheckJobRunning,
    DataflowTemplatedJobStartOperator,
)

with models.DAG(
    "gcp_dataflow_template_runner",
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

    def get_options(**kwargs):
        environment = kwargs['dag_run'].conf.get('environment')
        custom_parameters = kwargs['dag_run'].conf.get('parameters')
        Variable.set("custom_parameters", custom_parameters, serialize_json=True)
        Variable.set("environment", environment, serialize_json=True)

    print_options = PythonOperator(
        task_id='get_options', 
        python_callable=get_options, 
        dag=dag_template, 
        provide_context=True)

    stop_job = DataflowTemplatedJobStopOperator(
        task_id="stop-template-job",
        job_name="{{ dag_run.conf['job_name'] }}",
        project_id="{{ dag_run.conf['project_id'] }}",
        location="{{ dag_run.conf['location'] }}",
        drain_pipeline=False,
    )

    # https://github.com/apache/airflow/blob/0f327788b5b0887c463cb83dd8f732245da96577/airflow/providers/google/cloud/hooks/dataflow.py#L618
    start_job = DataflowTemplatedJobStartOperator(
        task_id="start-template-job",
        job_name="{{ dag_run.conf['job_name'] }}",
        append_job_name=False,
        template="{{ dag_run.conf['template'] }}",
        # https://cloud.google.com/dataflow/docs/reference/rest/v1b3/RuntimeEnvironment
        environment=Variable.get("environment", deserialize_json=True, default_var="{}"),
        parameters=Variable.get("custom_parameters", deserialize_json=True, default_var="{}"),
        location="{{ dag_run.conf['location'] }}",
    )

    print_content >> stop_job
    print_options >> stop_job
    stop_job >> start_job
