#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./project-id.txt

# set the active project
echo
echo setting active project to: ${PROJECT_ID}
echo
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Following instructions from:
# https://cloud.google.com/composer/docs/how-to/managing/creating#gcloud_1
# https://cloud.google.com/composer/docs/concepts/versioning/composer-versions#images
# https://cloud.google.com/composer/pricing#machine-type
# https://cloud.google.com/composer/pricing#db-machine-types
# https://cloud.google.com/composer/pricing#ws-machine-types

ENVIRONMENT_NAME=${PROJECT_ID}
LOCATION=us-central1
ZONE=us-central1-a
IMAGE_VERSION="composer-1.17.4-airflow-1.10.15"
NODE_COUNT=3
SCHEDULER_COUNT=1
DISK_SIZE=20
NODE_MACHINE_TYPE=n1-standard-2
SQL_MACHINE_TYPE=db-n1-standard-2
WS_MACHINE_TYPE=composer-n1-webserver-2

gcloud composer environments create ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    --zone     ${ZONE} \
    --image-version ${IMAGE_VERSION} \
    --node-count ${NODE_COUNT} \
    --disk-size ${DISK_SIZE} \
    --machine-type ${NODE_MACHINE_TYPE} \
    --cloud-sql-machine-type ${SQL_MACHINE_TYPE} \
    --web-server-machine-type ${WS_MACHINE_TYPE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# create bucket: https://cloud.google.com/storage/docs/quickstart-gsutil
BUCKET_NAME=gs://${PROJECT_ID}-bucket
gsutil mb -l ${LOCATION} -c standard ${BUCKET_NAME}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set AirFlow variables
gcloud composer environments run ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    variables -- \
    --set gcs_bucket ${BUCKET_NAME}

