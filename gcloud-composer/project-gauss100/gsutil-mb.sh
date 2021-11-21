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
### The following gsutil commands work on a Composer worker node

### copy (input) data from an existing Cloud Storage bucket
# mkdir ~/gcs/data/input ; gsutil cp gs://gauss100-2021-11-13-a-bucket/input/input-file-01.csv ~/gcs/data/input

### copy the worker node folder 'output-00' to a Cloud Storage bucket with a specified folder name ('output-00-a')
# gsutil cp -r ~/gcs/data/output-00 gs://gauss100-2021-11-13-a-bucket/output-00-a

