#!/bin/bash

source ./project-id.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
#  deleting project
echo
echo deleting project: ${PROJECT_ID}
echo
gcloud projects delete ${PROJECT_ID}

