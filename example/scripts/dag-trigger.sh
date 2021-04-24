#!/bin/bash

source _env/setup.sh
gsutil cp ../rollout.json gs://$RUN_CONFIG_BUCKET/rollout.json

