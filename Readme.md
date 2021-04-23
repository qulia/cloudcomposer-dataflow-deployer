# Setup

```
cd scripts
# create Dataflow template v1 
./template.sh

# deploy cloud functions fn
./cloud-functions-deploy.sh 

# Launch the pubsub publisher
./pubsub-publisher.sh

# Deploy the dag
./dag-deploy-test.sh
```


# Trigger 
```
# Trigger the dag to run job v1
./dag-trigger.sh
```
