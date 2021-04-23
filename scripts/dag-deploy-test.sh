#!/bin/bash

source _env/setup.sh
gsutil cp ../airflow/dataflow-deployer.py gs://$CLOUD_COMPOSER_BUCKET/dags/test/dataflow-deployer.py

gcloud composer environments run $CLOUD_COMPOSER_ENVIRONMENT_NAME \
 --location $CLOUD_COMPOSER_ENVIRONMENT_LOCATION  list_dags -- -sd /home/airflow/gcs/dags/test