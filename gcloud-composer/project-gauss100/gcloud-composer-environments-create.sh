#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

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
# set kubectl credentials (required by next command -- setting AirFlow variables)
CLUSTER_NAME=`gcloud container clusters list | tail -n +2 | awk '{print $1}'`
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# install Python dependencies
gcloud composer environments update ${ENVIRONMENT_NAME} \
   --update-pypi-packages-from-file python-dependencies.txt \
   --location ${LOCATION}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set AirFlow variables
gcloud composer environments run ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    variables -- \
    --set gcs_bucket ${BUCKET_NAME}

