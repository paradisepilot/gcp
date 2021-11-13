#!/bin/bash

PROJECT_ID=stc-eccc-gauss100

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
#  deleting 'stc-eccc-gauss100'
echo
echo deleting project: ${PROJECT_ID}
echo
gcloud projects delete ${PROJECT_ID}

