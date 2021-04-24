source _env/setup.sh

# Create a Pub/Sub topic.
gcloud pubsub topics create $TOPIC_ID

# Create a Cloud Scheduler job
gcloud scheduler jobs create pubsub publisher-job --schedule="* * * * *" \
  --topic=$TOPIC_ID --message-body="Hello"

# Run the job.
gcloud scheduler jobs run publisher-job