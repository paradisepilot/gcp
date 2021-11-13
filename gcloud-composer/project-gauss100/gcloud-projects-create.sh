#!/bin/bash

PROJECT_ID=stc-eccc-gauss100

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# create project to 'stc-eccc-gauss100'
echo
echo creating project: ${PROJECT_ID}
echo
gcloud projects create ${PROJECT_ID} \
    --name=${PROJECT_ID}

