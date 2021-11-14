#!/bin/bash

source ./global-parameters.txt

# delete environment
gcloud composer environments delete ${ENVIRONMENT_NAME} \
    --location ${LOCATION}

# remove environment's bucket
gsutil rb ${BUCKET_NAME}

# delete environment's disk
gcloud compute disks delete ${ENVIRONMENT_NAME} --zone=${ZONE}

