#!/bin/bash

source _env/setup.sh
gsutil cp -r ../../airflow/* gs://$CLOUD_COMPOSER_BUCKET/dags/

gcloud composer environments describe $CLOUD_COMPOSER_ENVIRONMENT_NAME \
 --location $CLOUD_COMPOSER_ENVIRONMENT_LOCATION --format="get(config.nodeConfig.serviceAccount)"

gcloud composer environments run $CLOUD_COMPOSER_ENVIRONMENT_NAME \
 --location $CLOUD_COMPOSER_ENVIRONMENT_LOCATION  list_dags -- -sd /home/airflow/gcs/dags