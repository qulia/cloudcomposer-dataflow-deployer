#!/bin/bash

source _env/setup.sh
gsutil cp ../run_v1.json gs://$RUN_CONFIG_BUCKET/run_v1.json

