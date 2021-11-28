#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

echo
echo PROJECT_ID=${PROJECT_ID}
echo ENVIRONMENT_NAME=${ENVIRONMENT_NAME}
echo LOCATION=${LOCATION}
echo ZONE=${ZONE}
echo BUCKET_NAME=${BUCKET_NAME}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set the active project
echo; echo Executing: gcloud config set project ${PROJECT_ID}
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

echo; echo Executing: gcloud composer environments create ${ENVIRONMENT_NAME} ...
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
# Use the gcloud composer command to connect the kubectl command to the cluster.
# https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#viewing_installed_python_packages

CLUSTER_NAME=`gcloud container clusters list | tail -n +2 | awk '{print $1}'`
echo; echo CLUSTER_NAME=${CLUSTER_NAME}

echo; echo Executing: gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
AIRFLOW_CLUSTER_NAMESPACE=`kubectl get namespaces | egrep 'airflow' | awk '{print $1}'`
echo; echo AIRFLOW_CLUSTER_NAMESPACE=${AIRFLOW_CLUSTER_NAMESPACE}

AIRFLOW_POD_NAME=`kubectl get pods -n ${AIRFLOW_CLUSTER_NAMESPACE} | egrep 'worker' | head -n 1 | awk '{print $1}'`
echo; echo AIRFLOW_POD_NAME=${AIRFLOW_POD_NAME}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Here, we include instructions for how to connect to an Airflow worker pod.

##### Opening a terminal to a worker node in a single command:
# AIRFLOW_CLUSTER_NAMESPACE=`kubectl get namespaces | egrep 'airflow' | awk '{print $1}'`; AIRFLOW_POD_NAME=`kubectl get pods -n ${AIRFLOW_CLUSTER_NAMESPACE} | egrep 'worker' | head -n 1 | awk '{print $1}'`; kubectl -n ${AIRFLOW_CLUSTER_NAMESPACE} exec -it ${AIRFLOW_POD_NAME} -c airflow-worker -- /bin/bash

##### Opening a terminal to a worker node manually in three commands:
##### (1) List the Kubernetes name spaces.
# kubectl get namespaces

##### (2) List the pods that are running in a given
#####     Kubernetes cluster namespace (composer-1-17-4-airflow-1-10-15-27457a66):
# kubectl get pods -n ${AIRFLOW_CLUSTER_NAMESPACE}
# kubectl get pods -n composer-1-17-4-airflow-1-10-15-27457a66

##### (3) Connect to a remote shell in an Airflow worker container:
#####     (Kubernetes cluster namespace: composer-1-17-4-airflow-1-10-15-27457a66)
#####     (Airflow worker pod name: airflow-worker-57ff5d7f48-22l9t)
# kubectl -n ${AIRFLOW_CLUSTER_NAMESPACE}             exec -it ${AIRFLOW_POD_NAME}             -c airflow-worker -- /bin/bash
# kubectl -n composer-1-17-4-airflow-1-10-15-27457a66 exec -it airflow-worker-57ff5d7f48-22l9t -c airflow-worker -- /bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
##### install Python dependencies
sleep 20
echo; echo Executing: gcloud composer environments update -- adding python dependencies
gcloud composer environments update ${ENVIRONMENT_NAME} --location ${LOCATION} \
    --update-pypi-packages-from-file python-dependencies.txt

### set environment variables
sleep 20
echo; echo Executing: gcloud composer environments update -- setting environment variables
gcloud composer environments update ${ENVIRONMENT_NAME} --location ${LOCATION} \
   --update-env-variables=EXTERNAL_BUCKET=${BUCKET_NAME},PROJECT_ID=${PROJECT_ID},ENVIRONMENT_NAME=${ENVIRONMENT_NAME},LOCATION=${LOCATION},ZONE=${ZONE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
##### creating two Kubernetes secrets:
##### (a)  Kubernetes secret environment variable that holds external bucket name
##### (b)  Kubernetes secret volume that holds service account key

# sleep 20
# cp ${SERVICE_ACCOUNT_KEY_JSON} service-account-key.json
#
# sleep 5
# echo;echo Executing: kubectl create secret generic airflow-secret ...
# kubectl create secret generic airflow-secret-external-bucket --from-literal external_bucket=${EXTERNAL_BUCKET}
#
# sleep 5
# echo;echo Executing: kubectl create secret generic airflow-secret-file ...
# kubectl create secret generic airflow-secret-file-service-account-key --from-file service_account_key=service-account-key.json
#
# sleep 5
# rm -f service-account-key.json
#
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set AirFlow variables
# sleep 20
# gcloud composer environments run ${ENVIRONMENT_NAME} \
#     --location ${LOCATION} \
#     variables -- \
#     --set gcs_bucket ${BUCKET_NAME}
