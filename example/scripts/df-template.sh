#!/bin/bash


source _env/setup.sh

gsutil mb gs://$ARTIFACTS_BUCKET
gsutil mb gs://$RESULTS_BUCKET
gsutil mb gs://$DATAFLOW_TEMPLATES_BUCKET

FILE_PATH=../PubSubToGCS.py
TEMPLATE_NAME=PubSubToGCS_v1

echo "$PROJECT_ID $BUCKET_NAME"

# create v1
python $FILE_PATH \
    --project=$PROJECT_ID \
    --runner=DataflowRunner \
    --input_topic=projects/$PROJECT_ID/topics/$TOPIC_ID \
    --output_path=gs://$RESULTS_BUCKET/out \
    --staging_location gs://$ARTIFACTS_BUCKET/staging \
    --temp_location gs://$ARTIFACTS_BUCKET/temp \
    --template_location gs://$DATAFLOW_TEMPLATES_BUCKET/$TEMPLATE_NAME

# create v2
TEMPLATE_NAME=PubSubToGCS_v2
python $FILE_PATH \
    --project=$PROJECT_ID \
    --runner=DataflowRunner \
    --input_topic=projects/$PROJECT_ID/topics/$TOPIC_ID \
    --output_path=gs://$RESULTS_BUCKET/out \
    --staging_location gs://$ARTIFACTS_BUCKET/staging \
    --temp_location gs://$ARTIFACTS_BUCKET/temp \
    --template_location gs://$DATAFLOW_TEMPLATES_BUCKET/$TEMPLATE_NAME

