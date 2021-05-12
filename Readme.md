# Cloud Composer Dataflow Deployer

Automating Dataflow job updates with Cloud Composer/Airflow. Read more at:

Folder structure:

- [airflow](airflow) folder contains the main DAG to orchestrate updating Dataflow jobs. The implementations of custom
  operators DataflowTemplatedJobStartOperator2 and DataflowTemplatedJobStopOperator are provided. These are used in the
  main DAG gcp_dataflow_template_deployer.

- [cloud-functions](cloud-functions) folder contains the logic to externally trigger the DAG upon Cloud Storage bucket's
  create/update event. Deploy configs like [rollout.json](example/rollout.json) is pushed to the bucket, which triggers
  the cloud function.

- [example](example) folder contains an end to end example on how to provision GCP resources and triggering deployments
  with a single command, and the manifest file which has the runtime parameters and configuration. The Dataflow job is
  extended from [this example](https://cloud.google.com/pubsub/docs/pubsub-dataflow#python) to include runtime value
  providers. 
