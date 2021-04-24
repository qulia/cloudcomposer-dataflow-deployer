# Setup

- Create setup.sh under example/scripts/_env dir as bellow 
and fill in the empty values and replace the others as needed.

```
#!/bin/bash

export JOB=pubsub-to-gcs
export ARTIFACTS_BUCKET=$JOB-artifacts
export DATAFLOW_TEMPLATES_BUCKET=$JOB-dataflow-templates
export RESULTS_BUCKET=$JOB-results
export PROJECT_ID=dataflow-airflow
export TOPIC_ID=$JOB-topic

export RUN_CONFIG_BUCKET=$JOB-run-config

export CLOUD_COMPOSER_ENVIRONMENT_NAME=
export CLOUD_COMPOSER_ENVIRONMENT_LOCATION=
export CLOUD_COMPOSER_BUCKET=

#https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf#get_the_client_id_of_the_iam_proxy
export CLOUD_COMPOSER_CLIENT_ID=
export CLOUD_COMPOSER_WEBSERVER_ID=

export DAG_NAME=gcp_dataflow_template_runner
```
- Run the following commands for one time setup of the example.

```
cd example/scripts
# create Dataflow templates for the Dataflow jobs 
./df-template.sh

# deploy cloud functions fn, this will get triggered when new run config is pushed to the bucket
./cloud-functions-deploy.sh 

# Launch the pubsub publisher, the events will be used by the Dataflow job
./pubsub-publisher.sh

# Deploy the dag and validate. The DAG will get triggered by cloud function to update the Dataflow job
./dag-deploy-validate.sh
```

# Trigger 

Deploy and each time you need to deploy config/code updates use the following. 

```
# Trigger the dag to deploy, updating rollout.json accordingly
# The dag will stop the Dataflow job running (if any) with spec "from" and launch with spec "to"
# Check the jobs in Dataflow UI and DAG status in Airflow UI of Cloud Composer environment
./dag-trigger.sh
```
