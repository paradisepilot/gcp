#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

# set the active project
echo
echo setting active project to: ${PROJECT_ID}
echo
gcloud config set project ${PROJECT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### upload a DAG to Composer environment
gcloud composer environments storage dags import \
    --environment ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    --source dag-gauss100.py

