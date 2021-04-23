from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators import PythonOperator
from airflow.models import Variable

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
        dataflow_default_options = kwargs['dag_run'].conf.get('dataflow_default_options') 
        custom_parameters = kwargs['dag_run'].conf.get('parameters') 
        Variable.set("custom_parameters", custom_parameters, serialize_json=True)
        Variable.set("dataflow_default_options", dataflow_default_options, serialize_json=True)

    print_options = PythonOperator(
        task_id='get_options', 
        python_callable=get_options, 
        dag=dag_template, 
        provide_context=True)

    start_job = DataflowTemplatedJobStartOperator(
        task_id="start-template-job",
        job_name="{{ dag_run.conf['job_name'] }}",
        template="{{ dag_run.conf['template'] }}",
        dataflow_default_options=Variable.get("dataflow_default_options", deserialize_json=True),
        parameters=Variable.get("custom_parameters", deserialize_json=True, default_var="{}"),
        location="{{ dag_run.conf['location'] }}",
    )

    print_content >> start_job
    print_options >> start_job
