#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

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

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### create service account

# echo;echo gcloud iam service-accounts create ${SERVICE_ACCOUNT_ID} --display-name=${SERVICE_ACCOUNT_ID}
# gcloud iam service-accounts create ${SERVICE_ACCOUNT_ID} --display-name=${SERVICE_ACCOUNT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### list service accounts

# echo;echo gcloud iam service-accounts list
# gcloud iam service-accounts list

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### grant binding to ${EXTERNAL_BUCKET}:
### https://cloud.google.com/iam/docs/creating-managing-service-accounts#iam-service-accounts-create-gcloud
### https://cloud.google.com/iam/docs/understanding-roles

# echo;echo gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin ${EXTERNAL_BUCKET} 
# gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin ${EXTERNAL_BUCKET} 

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### get IAM permissions of external bucket

# echo;echo gsutil iam get ${EXTERNAL_BUCKET}
# gsutil iam get ${EXTERNAL_BUCKET}

