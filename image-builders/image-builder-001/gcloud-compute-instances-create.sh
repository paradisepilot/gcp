#!/bin/bash

gcloud compute instances create voyager \
    --zone               northamerica-northeast1-a \
    --machine-type       n1-standard-1 \
    --image              ubuntu-1804-bionic-v20181024 \
    --image-project      ubuntu-os-cloud \
    --metadata-from-file startup-script=myStartupScript.sh

