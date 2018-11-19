#!/bin/bash

# https://cloud.google.com/compute/docs/disks/create-root-persistent-disks
gcloud compute disks create vdisk01 \
    --image         vimg01 \
    --image-project alert-basis-204816 \
    --zone          northamerica-northeast1-c \
    --size          200GB

