#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

# set the active project
echo; echo setting active project to: ${PROJECT_ID}
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### upload a DAG to Composer environment
echo; echo Executing: gcloud composer environments storage dags import
gcloud composer environments storage dags import \
    --environment ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    --source dag-fpca.py

