#!/bin/bash

source ./global-parameters.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# create project
echo
echo creating project: ${PROJECT_ID}
echo
gcloud projects create ${PROJECT_ID} --name=${PROJECT_ID}

