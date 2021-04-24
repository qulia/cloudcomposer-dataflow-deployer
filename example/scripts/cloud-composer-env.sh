#!/bin/bash

source _env/setup.sh

gcloud composer environments create $CLOUD_COMPOSER_ENVIRONMENT_NAME \
    --location $CLOUD_COMPOSER_ENVIRONMENT_LOCATION \
    --airflow-configs api-auth_backend=airflow.api.auth.backend.default

gcloud composer environments describe $CLOUD_COMPOSER_ENVIRONMENT_NAME \
    --location $CLOUD_COMPOSER_ENVIRONMENT_LOCATION \
    --format='value(config.airflowUri)'