#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

# set the active project
echo
echo setting active project to: ${PROJECT_ID}
echo
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### create bucket: https://cloud.google.com/storage/docs/quickstart-gsutil
# gsutil mb -l ${LOCATION} -c standard ${BUCKET_NAME}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### upload data to bucket
# gsutil -m cp -r input-files ${BUCKET_NAME}/input

### ########################################### ###
### The following gsutil commands work on a Composer worker node.
###
### Below, we assume the following environment variables have been set:
###     EXTERNAL_BUCKET=gs://gauss100-2021-11-13-a-bucket
###     PROJECT_ID=gauss100-2021-11-13-a
###     ENVIRONMENT_NAME=gauss100-2021-11-13-a
###     LOCATION=us-central1
###     ZONE=us-central1-a
###

### list contents of a bucket folder
# gsutil ls ${EXTERNAL_BUCKET}/input/input*

### copy (input) folder from an existing Cloud Storage bucket
# gsutil cp -r ${EXTERNAL_BUCKET}/input gcs/data

### copy (input) file from an existing Cloud Storage bucket
# gsutil cp ${EXTERNAL_BUCKET}/input/input-file-01.csv gcs/data/input

### copy the worker node folder to a Cloud Storage bucket with a specified folder name ('output')
# gsutil cp -r gcs/data/output ${EXTERNAL_BUCKET}/output

