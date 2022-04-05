
# from datetime import timedelta, datetime
import datetime

from airflow import models
from airflow.operators.bash_operator   import BashOperator
from airflow.operators.dummy_operator  import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.models import Variable
# from airflow.kubernetes.secret import Secret
from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount

import os

bucket_list = ['fpca-bay-of-quinte-test','fpca-williston-a']

JOB_NAME = 'fpca_gke'

start_date = datetime.datetime(2021, 1, 31)
# YESTERDAY = datetime.now() - timedelta(days=1)

default_args = {
    # 'start_date': YESTERDAY,
    'start_date': start_date,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=1)
}

with models.DAG(JOB_NAME,
                default_args=default_args,
                schedule_interval=None,
                # schedule_interval=timedelta(days=1),
                concurrency=3,
                catchup=False
                ) as dag:

    # This value can be customized to whatever format is preferred for the node pool name
    # Default node pool naming format is <cluster name>-node-pool-<execution_date>
    # node_pool_value = "$COMPOSER_ENVIRONMENT-node-pool-$(echo {{ ts_nodash }} | awk '{print tolower($0)}')"
    node_pool_value = "ndpl-$(echo {{ ts_nodash }} | awk '{print tolower($0)}')"

    create_node_pool_command = """
    # Set some environment variables in case they were not set already

    # [ -z "${NODE_COUNT}" ] && NODE_COUNT=6
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=n1-standard-2
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-4-5120
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-16-65536
    # [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-80-262144
    # [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=20
    # [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=512

    [ -z "${NODE_COUNT}" ] && NODE_COUNT=3
    [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=custom-4-5120
    [ -z "${SCOPES}" ] && SCOPES=default,cloud-platform
    [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=20

    # Generate node-pool name
    NODE_POOL=""" + node_pool_value + """

    echo;echo whoami=`whoami`
    echo;echo pwd; pwd
    echo;echo cd /home/airflow/; cd /home/airflow/
    echo;echo pwd; pwd

    echo;echo COMPOSER_GKE_ZONE=${COMPOSER_GKE_ZONE}
    echo;echo COMPOSER_GKE_NAME=${COMPOSER_GKE_NAME}
    echo;echo CLUSTER_NAME=${CLUSTER_NAME}
    echo;echo NODE_POOL=${NODE_POOL}
    echo;echo MACHINE_TYPE=${MACHINE_TYPE}
    echo;echo NODE_COUNT=${NODE_COUNT}
    echo;echo NODE_DISK_SIZE=${NODE_DISK_SIZE}
    echo;echo SCOPES=${SCOPES}

    ### It is important to set container/cluster; otherwise, Composer would
    ### throw an error at the node pool creation command below
    ### due to the fact that the node pool creation would require more vCPU
    ### than regional vCPU quota.
    echo;echo Executing: sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    sleep 10

    ### set kubectl credentials (required by subsequent commands)
    ### Use the gcloud composer command to connect the kubectl command to the cluster.
    ### https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#viewing_installed_python_packages
    echo;echo Executing: sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

    sleep 10

    echo;echo Executing: gcloud container node-pools create ${NODE_POOL} ...
    gcloud container node-pools create ${NODE_POOL} \
        --project=${GCP_PROJECT}       --cluster=${COMPOSER_GKE_NAME} --zone=${COMPOSER_GKE_ZONE} \
        --machine-type=${MACHINE_TYPE} --num-nodes=${NODE_COUNT}      --disk-size=${NODE_DISK_SIZE} \
        --enable-autoscaling --min-nodes 1 --max-nodes ${NODE_COUNT} \
        --scopes=${SCOPES} \
        --enable-autoupgrade

    ### Set the airflow variable name
    echo;echo Executing: airflow variables -s node_pool ${NODE_POOL}
    airflow variables -s node_pool ${NODE_POOL}

    sleep 10

    ### Examine clusters
    echo;echo Executing: gcloud container clusters list
    gcloud container clusters list

    sleep 10

    ### Examine Kubernetes namespaces
    echo;echo Executing: kubectl get namespaces
    kubectl get namespaces

    sleep 10

    ### create Kubernetes secret environment variable for EXTERNAL_BUCKET, and
    ### create Kubernetes secret volume for service account key
    # echo;echo Executing: pwd
    # pwd
    # echo;echo Executing: gsutil cp ${EXTERNAL_BUCKET}/secrets/service-account-key.json .
    # gsutil cp ${EXTERNAL_BUCKET}/secrets/service-account-key.json .
    # sleep 5
    # echo;echo Executing: ls -l service-account-key.json
    # ls -l service-account-key.json
    # echo;echo Executing: kubectl create secret generic airflow-secrets-fpca ...
    # kubectl create secret generic airflow-secrets-fpca \
    #    --from-literal=external_bucket=${EXTERNAL_BUCKET} \
    #    --from-file=service-account-key.json
    # sleep 5
    # rm -f service-account-key.json

    ### check Kubernetes secrets
    # echo;echo Executing: kubectl get secrets
    # kubectl get secrets
    """

    delete_node_pools_command = """
    # Generate node-pool name
    NODE_POOL=""" + node_pool_value + """

    echo; echo >> gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    echo;echo Executing: gcloud container node-pools delete ${NODE_POOL} --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet
    sudo gcloud container node-pools delete ${NODE_POOL} --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet
    """

    injest_input_data_command = """
echo \
"\n\
apiVersion: storage.k8s.io/v1\n\
kind: StorageClass\n\
metadata:\n\
  name: my-storage-class\n\
  namespace: default\n\
provisioner: kubernetes.io/gce-pd\n\
parameters:\n\
  type: pd-ssd\n"\
> create_sc.yaml

echo \
"\n\
apiVersion: v1\n\
kind: PersistentVolumeClaim\n\
metadata:\n\
  name: pvc-{BUCKET_NAME}\n\
  namespace: default\n\
spec:\n\
  resources:\n\
    requests:\n\
      storage: 64Gi\n\
  accessModes:\n\
    - ReadWriteOnce\n\
  storageClassName: my-storage-class\n"\
> create_pvc.yaml

echo \
"\n\
apiVersion: v1\n\
kind: Pod\n\
metadata:\n\
  name: pd-{BUCKET_NAME}\n\
  namespace: default\n\
spec:\n\
  containers:\n\
  - name: datatransfer-container\n\
    image: nginx\n\
    volumeMounts:\n\
    - mountPath: /datatransfer\n\
      name: script-data\n\
  volumes:\n\
  - name: script-data\n\
    persistentVolumeClaim:\n\
      claimName: pvc-{BUCKET_NAME}\n"\
> create_pod_data.yaml

    echo;echo cat create_sc.yaml
    cat create_sc.yaml
    echo

    echo;echo cat create_pvc.yaml
    cat create_pvc.yaml
    echo

    echo;echo cat create_pod_data.yaml
    cat create_pod_data.yaml
    echo

    sleep 10

    echo; echo Executing: gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sleep 10

    echo;echo Executing: sudo kubectl create -f create_sc.yaml
    sudo kubectl create -f create_sc.yaml
    sleep 10

    echo;echo Executing: sudo kubectl create -f create_pvc.yaml
    sudo kubectl create -f create_pvc.yaml
    sleep 10

    echo;echo Executing: sudo kubectl create -f create_pod_data.yaml
    sudo kubectl create -f create_pod_data.yaml
    sleep 10

    echo;echo Executing: sudo kubectl get nodes ; echo ; sudo kubectl get pods -o wide
    sudo kubectl get nodes ; echo ; sudo kubectl get pods -o wide
    sleep 10

    # Assume that the environment variable BUCKET has been set.
    echo;echo BUCKET_NAME={BUCKET_NAME}

    echo;echo Executing: gsutil ls {BUCKET_NAME}/TrainingData_Geojson
    gsutil ls {BUCKET_NAME}/TrainingData_Geojson

    echo;echo Executing: mkdir datatransfer
    mkdir datatransfer

    echo;echo Executing: gsutil -m cp -r gs://{BUCKET_NAME}/TrainingData_Geojson datatransfer
    gsutil -m cp -r gs://{BUCKET_NAME}/TrainingData_Geojson datatransfer

    echo;echo Executing: sudo kubectl cp datatransfer/TrainingData_Geojson default/pd-{BUCKET_NAME}:/datatransfer
    sudo kubectl cp datatransfer/TrainingData_Geojson default/pd-{BUCKET_NAME}:/datatransfer

    # echo;echo Executing: gsutil -m cp -r gs://{BUCKET_NAME}/img datatransfer
    # gsutil -m cp -r gs://{BUCKET_NAME}/img datatransfer

    # echo;echo Executing: sudo kubectl cp datatransfer/img default/pd-{BUCKET_NAME}:/datatransfer
    # sudo kubectl cp datatransfer/img default/pd-{BUCKET_NAME}:/datatransfer

    echo;echo Executing: ls -l datatransfer
    ls -l datatransfer

    echo;echo Executing: ls -l datatransfer/*
    ls -l datatransfer/*
    """

    delete_datatransfer_pod_command = """
    echo;echo Executing: sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    sudo gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    sleep 10

    echo;echo Executing: sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sleep 10

    # Generate node-pool name
    NODE_POOL=""" + node_pool_value + """

    ### Set the airflow variable name
    echo;echo Executing: airflow variables -s node_pool ${NODE_POOL}
    airflow variables -s node_pool ${NODE_POOL}
    sleep 10

    ### Examine clusters
    echo;echo Executing: gcloud container clusters list
    gcloud container clusters list
    sleep 10

    echo;echo Executing: sudo kubectl get nodes
    sudo kubectl get nodes

    echo;echo Executing: sudo kubectl get pods -o wide
    sudo kubectl get pods -o wide

    echo;echo Executing: sudo kubectl delete pod pd-{BUCKET_NAME}
    sudo kubectl delete pod pd-{BUCKET_NAME}
    """

    persist_output_data_command = """
echo \
"\n\
apiVersion: storage.k8s.io/v1\n\
kind: StorageClass\n\
metadata:\n\
  name: my-storage-class\n\
  namespace: default\n\
provisioner: kubernetes.io/gce-pd\n\
parameters:\n\
  type: pd-ssd\n"\
> create_sc.yaml

echo \
"\n\
apiVersion: v1\n\
kind: PersistentVolumeClaim\n\
metadata:\n\
  name: pvc-{BUCKET_NAME}\n\
  namespace: default\n\
spec:\n\
  resources:\n\
    requests:\n\
      storage: 64Gi\n\
  accessModes:\n\
    - ReadWriteOnce\n\
  storageClassName: my-storage-class\n"\
> create_pvc.yaml

echo \
"\n\
apiVersion: v1\n\
kind: Pod\n\
metadata:\n\
  name: pd-{BUCKET_NAME}\n\
  namespace: default\n\
spec:\n\
  containers:\n\
  - name: datatransfer-container\n\
    image: nginx\n\
    volumeMounts:\n\
    - mountPath: /datatransfer\n\
      name: script-data\n\
  volumes:\n\
  - name: script-data\n\
    persistentVolumeClaim:\n\
      claimName: pvc-{BUCKET_NAME}\n"\
> create_pod_data.yaml

    echo;echo cat create_sc.yaml
    cat create_sc.yaml
    echo

    echo;echo cat create_pvc.yaml
    cat create_pvc.yaml
    echo

    echo;echo cat create_pod_data.yaml
    cat create_pod_data.yaml
    echo
    sleep 10

    echo; echo Executing: gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sudo gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    sleep 10

    echo;echo Executing: sudo kubectl create -f create_sc.yaml
    # sudo kubectl create -f create_sc.yaml
    sleep 10

    echo;echo Executing: sudo kubectl create -f create_pvc.yaml
    # sudo kubectl create -f create_pvc.yaml
    sleep 10

    echo;echo Executing: sudo kubectl create -f create_pod_data.yaml
    sudo kubectl create -f create_pod_data.yaml
    sleep 10

    echo;echo Executing: sudo kubectl get nodes
    sudo kubectl get nodes
    sleep 10

    echo;echo Executing: sudo kubectl get pods -o wide
    sudo kubectl get pods -o wide
    sleep 10

    echo;echo Executing: mkdir -p datatransfer/output
    mkdir -p datatransfer/output
    sleep 10

    echo;echo Executing: ls -l
    ls -l
    sleep 10

    echo;echo Executing: ls -l datatransfer
    ls -l datatransfer
    sleep 10

    echo;echo Executing: sudo kubectl cp default/pd-{BUCKET_NAME}:/datatransfer/output datatransfer/output
    sudo kubectl cp default/pd-{BUCKET_NAME}:/datatransfer/output datatransfer/output
    sleep 10

    echo;echo Executing: ls -l datatransfer
    ls -l datatransfer
    sleep 10

    echo;echo Executing: ls -l datatransfer/output
    ls -l datatransfer/output
    sleep 10

    # Assume that the environment variable EXTERNAL_BUCKET has been set.
    echo;echo Executing: gsutil -m cp -r datatransfer/output ${EXTERNAL_BUCKET}
    gsutil -m cp -r "datatransfer/output/*" ${EXTERNAL_BUCKET}/output/{BUCKET_NAME}
    sleep 10

    echo;echo Executing: gsutil ls ${EXTERNAL_BUCKET}
    gsutil ls ${EXTERNAL_BUCKET}
    sleep 10

    echo;echo Executing: gsutil ls ${EXTERNAL_BUCKET}/output
    gsutil ls ${EXTERNAL_BUCKET}/output
    sleep 10

    echo;echo Executing: sudo kubectl delete pod pd-{BUCKET_NAME}
    sudo kubectl delete pod pd-{BUCKET_NAME}

    echo;echo Executing: sudo kubectl get nodes
    sudo kubectl get nodes
    sleep 10

    echo;echo Executing: sudo kubectl get pods -o wide
    sudo kubectl get pods -o wide
    sleep 10
    """

    # Tasks definitions
    start_task = DummyOperator(
        task_id="start"
        )

    end_task = DummyOperator(
        task_id="end"
        )

    create_node_pool_task = BashOperator(
        task_id      = "create_node_pool",
        bash_command = create_node_pool_command,
        xcom_push    = True,
        dag          = dag
    )

    delete_node_pool_task = BashOperator(
        task_id      = "delete_node_pool",
        bash_command = delete_node_pools_command,
        trigger_rule = 'all_done', # Always run even if failures so the node pool is deleted
        # xcom_push  = True,
        dag          = dag
    )

    injest_input_data_tasks       = []
    delete_datatransfer_pod_tasks = []
    fpca_tasks                    = []
    persist_output_data_tasks     = []

    for BUCKET_NAME in bucket_list:

        my_disk_claim = 'pvc-' + BUCKET_NAME;

        volume_config = {'persistentVolumeClaim':{'claimName': my_disk_claim}}
        volume        = Volume(name = my_disk_claim, configs = volume_config)
        volume_mount  = VolumeMount(my_disk_claim, mount_path = '/datatransfer',sub_path = None, read_only = False)

        injest_input_data_tasks.append(BashOperator(
            task_id      = "injest_input_data_{}".format(BUCKET_NAME),
            bash_command = injest_input_data_command.replace("{BUCKET_NAME}",BUCKET_NAME),
            xcom_push    = True,
            dag          = dag
        ))

        delete_datatransfer_pod_tasks.append(BashOperator(
            task_id      = "delete_datatransfer_pod_{}".format(BUCKET_NAME),
            bash_command = delete_datatransfer_pod_command.replace("{BUCKET_NAME}",BUCKET_NAME),
            xcom_push    = True,
            dag          = dag
        ))

        fpca_tasks.append(kubernetes_pod.KubernetesPodOperator(
            task_id   = 'fpca_{}'.format(BUCKET_NAME),
            name      = 'fpca_{}'.format(BUCKET_NAME),
            namespace = 'default',
            image     = 'paradisepilot/fpca-base:0.8',
            cmds      = ["sh", "-c", 'echo \'Sleeping ...\'; sleep 10; echo;echo which docker ; which docker; echo;echo which R ; which R ; echo;echo R -e "library(help=arrow)" ; R -e "library(help=arrow)"; echo;echo R -e "library(help=fpcFeatures)" ; R -e "library(help=fpcFeatures)"; echo;echo ls -l /home/airflow/gcs/data/ ; ls -l /home/airflow/gcs/data/ ; echo;echo ls -l /datatransfer/TrainingData_Geojson ; ls -l /datatransfer/TrainingData_Geojson/ ; echo;echo mkdir github ; mkdir github ; echo;echo cd github ; cd github ; echo;echo git clone https://github.com/STC-NWRC/bay-of-quinte.git ; git clone https://github.com/STC-NWRC/bay-of-quinte.git ; echo;echo cd bay-of-quinte ; cd bay-of-quinte ; echo;echo chmod ugo+x run-main.sh ; chmod ugo+x run-main.sh ;  echo;echo ./run-main.sh orange ; ./run-main.sh orange ; echo;echo pwd ; pwd ; echo;echo "ls -l .." ; ls -l .. ; echo;echo "ls -l ../.." ; ls -l ../.. ; echo;echo "tree ../.." ; tree ../.. ; echo;echo "cat ../../gittmp/bay-of-quinte/output-orange/stdout.R.main" ; cat ../../gittmp/bay-of-quinte/output-orange/stdout.R.main ; echo;echo "cd ../.." ; cd ../.. ; echo;echo pwd ; pwd ; echo;echo ls -l ; ls -l ; mkdir /datatransfer/output ; echo;echo rm -rf /datatransfer/output/output-orange; rm -rf /datatransfer/output/output-orange ; echo;echo cp -r gittmp/bay-of-quinte/output-orange /datatransfer/output/output-orange ; cp -r gittmp/bay-of-quinte/output-orange /datatransfer/output/output-orange ; echo;echo "ls -l /datatransfer/output/" ; ls -l /datatransfer/output/ ; echo;echo "ls -l /datatransfer/output/output-orange" ; ls -l /datatransfer/output/output-orange ; echo;echo \'Done!\''],
            startup_timeout_seconds = 86400,
            volumes       = [volume],
            volume_mounts = [volume_mount],
          # resources={'request_cpu': "15000m", 'request_memory': "61440M"},
            resources = {'request_cpu':  "3000m", 'request_memory':  "3072M"},
            tolerations = [{
                'key': "work",
                'operator': 'Equal',
                'value': 'well',
                'effect': "NoSchedule"
                }],
            affinity = {
                'nodeAffinity': {
                    'requiredDuringSchedulingIgnoredDuringExecution': {
                        'nodeSelectorTerms': [{
                            'matchExpressions': [{
                                'key': 'cloud.google.com/gke-nodepool',
                                'operator': 'In',
                                'values': [
                                    Variable.get("node_pool", default_var=node_pool_value)
                                ]
                            }]
                        }]
                    }
                }
            }
        ))

        persist_output_data_tasks.append(BashOperator(
            task_id      = "persist_output_data_{}".format(BUCKET_NAME),
            bash_command = persist_output_data_command.replace("{BUCKET_NAME}",BUCKET_NAME),
            xcom_push    = True,
            dag          = dag
        ))

    # Tasks order
    start_task >> create_node_pool_task

    for i in range(0,len(fpca_tasks)):
        create_node_pool_task >> injest_input_data_tasks[i] >> delete_datatransfer_pod_tasks[i] >> fpca_tasks[i] >> persist_output_data_tasks[i] >> delete_node_pool_task

    delete_node_pool_task >> end_task
