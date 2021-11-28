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
###     SERVICE_ACCOUNT_ID=gauss100-service-account
###

### ########################################### ###
###
### In order to allow a Kubernetes pod to read from and write to the project
### external bucket, proceed as follows:
### (a)  Create a service account.
### (b)  Create a service account key (JSON) for the service account in (a).
### (c)  Assign Object Admin role to the service accounta; add resulting IAM
###      policy to external bucket.
### (d)  Transfer -- via Kubernetes secret -- the service account key (JSON) to
###      each Kubernetes pod that needs to read from or write to project external
###      bucket.
### (e)  On each such Kubernetes pod, activate service account.
###

### ########################################### ###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (a)  Create service account.

# echo;echo gcloud iam service-accounts create ${SERVICE_ACCOUNT_ID} --display-name=${SERVICE_ACCOUNT_ID}
# gcloud iam service-accounts create ${SERVICE_ACCOUNT_ID} --display-name=${SERVICE_ACCOUNT_ID}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (b)  Create service account key.
###
### Visit the following web page:
### https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### list service accounts

# echo;echo gcloud iam service-accounts list
# gcloud iam service-accounts list

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (c)  Assign Object Admin role to the service accounta; add resulting IAM policy to project external bucket.
###
### grant binding to ${EXTERNAL_BUCKET}:
### https://cloud.google.com/iam/docs/creating-managing-service-accounts#iam-service-accounts-create-gcloud
### https://cloud.google.com/iam/docs/understanding-roles

# echo;echo gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin ${EXTERNAL_BUCKET} 
# gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:objectAdmin ${EXTERNAL_BUCKET} 

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### get IAM permissions of external bucket

# echo;echo gsutil iam get ${EXTERNAL_BUCKET}
# gsutil iam get ${EXTERNAL_BUCKET}

### ########################################### ###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (d)  Transfer service account key to Kubernetes pods.

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### (e)  On each such Kubernetes pod, activate service account.
###
### The following gcloud is to be run on each Kubernetes pod that needs to read
### from or write to the project external bucket.

# gcloud auth activate-service-account --key-file /var/secrets/google/gauss100-2021-11-13-a-f52029c2c997.json

