#!/bin/bash

gcloud compute instances create voyager \
    --zone               northamerica-northeast1-c \
    --machine-type       n1-standard-1 \
    --image              ubuntu-1810-cosmic-v20181018 \
    --image-project      ubuntu-os-cloud \
    --boot-disk-size     100GB \
    --metadata-from-file startup-script=myStartupScript.sh

