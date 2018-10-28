#!/bin/bash

gcloud compute instances create voyager \
    --zone          northamerica-northeast1-a \
    --machine-type  n1-standard-1 \
    --image         ubuntu-minimal-1810-cosmic-v20181018 \
    --image-project ubuntu-os-cloud \
    --metadata      startup-script=my-startup-script.sh

