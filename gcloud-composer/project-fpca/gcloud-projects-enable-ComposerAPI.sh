#!/bin/bash

source ./global-parameters.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# following instructions from: https://cloud.google.com/endpoints/docs/openapi/enable-api
echo
echo list projects:
gcloud projects list

# set the active project 
echo
echo setting active project to: ${PROJECT_ID}
echo
gcloud config set project ${PROJECT_ID}

# list the API's that can be enabled for the active project
echo
echo capturing available services for project ${PROJECT_ID} to stdout.gcloud-services-list-available
echo
gcloud services list --available > stdout.gcloud-services-list-available

# enable the Google Cloud Composer API for the active project
SERVICE_NAME=composer.googleapis.com
echo
echo enabling the serivce ${SERVICE_NAME} for project ${PROJECT_ID}
echo
gcloud services enable ${SERVICE_NAME}

