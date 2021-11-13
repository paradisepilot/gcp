#!/bin/bash

gcloud compute images create vimg01 \
    --source-disk        voyager \
    --source-disk-zone   northamerica-northeast1-c \
    --force

