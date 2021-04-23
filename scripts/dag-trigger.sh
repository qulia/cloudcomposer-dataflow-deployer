#!/bin/bash

source _env/setup.sh
gsutil cp ../airflow/run_v1.json gs://$RUN_CONFIG_BUCKET/run_v1.json

