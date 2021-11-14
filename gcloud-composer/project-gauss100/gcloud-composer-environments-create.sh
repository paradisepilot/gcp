#!/bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ./global-parameters.txt

# set the active project
echo
echo setting active project to: ${PROJECT_ID}
echo
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
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Here, we include instructions for how to connect to an Airflow worker pod.

##### (1) List the pods that are running in a given
#####     Kubernetes cluster namespace (composer-1-17-4-airflow-1-10-15-27457a66):
# kubectl get pods -n composer-1-17-4-airflow-1-10-15-27457a66

##### (2) Connect to a remote shell in an Airflow worker container:
#####     (Kubernetes cluster namespace: composer-1-17-4-airflow-1-10-15-27457a66)
#####     (Airflow worker pod name: airflow-worker-57ff5d7f48-22l9t)
# kubectl -n composer-1-17-4-airflow-1-10-15-27457a66 exec -it airflow-worker-57ff5d7f48-22l9t -c airflow-worker -- /bin/bash

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# install Python dependencies
gcloud composer environments update ${ENVIRONMENT_NAME} \
   --update-pypi-packages-from-file python-dependencies.txt \
   --location ${LOCATION}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# set AirFlow variables
gcloud composer environments run ${ENVIRONMENT_NAME} \
    --location ${LOCATION} \
    variables -- \
    --set gcs_bucket ${BUCKET_NAME}

