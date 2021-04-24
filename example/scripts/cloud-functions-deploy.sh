#!/bin/bash

source _env/setup.sh

gsutil mb gs://$RUN_CONFIG_BUCKET

gcloud functions deploy cloudcomposer-trigger-fn --source ../../cloud-functions \
 --region $CLOUD_COMPOSER_ENVIRONMENT_LOCATION --entry-point trigger_dag --runtime python37 --trigger-bucket $RUN_CONFIG_BUCKET \
 --set-env-vars=CLOUD_COMPOSER_CLIENT_ID=$CLOUD_COMPOSER_CLIENT_ID,CLOUD_COMPOSER_WEBSERVER_ID=$CLOUD_COMPOSER_WEBSERVER_ID,DAG_NAME=$DAG_NAME