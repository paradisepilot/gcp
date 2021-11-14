#!/bin/bash

source ./global-parameters.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# delete environment
gcloud composer environments delete ${ENVIRONMENT_NAME} \
    --location ${LOCATION}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# delete environment's disks

echo
gcloud compute disks list
echo

DISK_NAMES=(`gcloud compute disks list | tail -n +2 | awk '{print $1}'`)
for diskname in "${DISK_NAMES[@]}"
do
    echo deleting disk: ${diskname}
    gcloud compute disks delete ${diskname} --zone=${ZONE}
done

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# remove environment's bucket
# gsutil rb ${BUCKET_NAME}

