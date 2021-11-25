#!/bin/bash

gcloud container node-pools delete `gcloud container node-pools list --zone=us-central1-a | egrep -v '(NAME|default-pool)' | awk '{print $1}'` --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet

