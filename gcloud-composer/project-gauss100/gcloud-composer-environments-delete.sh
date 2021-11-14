#!/bin/bash

source ./project-id.txt

ENVIRONMENT_NAME=${PROJECT_ID}
LOCATION=us-central1
ZONE=us-central1-a

# delete environment
gcloud composer environments delete ${ENVIRONMENT_NAME} \
    --location ${LOCATION}

# remove environment's bucket
BUCKET_NAME=`gsutil ls`
gsutil rb ${BUCKET_NAME}

# delete environment's disk
gcloud compute disks delete ${ENVIRONMENT_NAME} --zone=${ZONE}

