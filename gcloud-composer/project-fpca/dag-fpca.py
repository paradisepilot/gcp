
# from datetime import timedelta, datetime
import datetime

from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.models import Variable
# from airflow.kubernetes.secret import Secret
from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount

import os

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

# secret_envvar_external_bucket = Secret(
#     # Name of the Kubernetes Secret
#     secret='airflow-secrets-fpca',
#     # Expose the secret as environment variable.
#     deploy_type='env',
#     # Key of a secret stored in this Secret object
#     key='external_bucket',
#     # The name of the environment variable, since deploy_type is `env` rather than `volume`.
#     deploy_target='EXTERNAL_BUCKET'
#     )
#
# secret_volume_service_account_key = Secret(
#     # Name of Kubernetes Secret
#     secret='airflow-secrets-fpca',
#     # type of secret
#     deploy_type='volume',
#     # Key in the form of service account file name
#     key='service-account-key.json',
#     # Path where we mount the secret as volume
#     deploy_target='/var/secrets/google'
#     )

volume_config = {'persistentVolumeClaim':{'claimName': 'my-disk-claim'}}
volume        = Volume(name = 'my-disk-claim', configs = volume_config)
volume_mount  = VolumeMount('my-disk-claim', mount_path = '/datatransfer',sub_path = None, read_only = False)

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
  name: my-disk-claim\n\
  namespace: default\n\
spec:\n\
  resources:\n\
    requests:\n\
      storage: 500Gi\n\
  accessModes:\n\
    - ReadWriteOnce\n\
  storageClassName: my-storage-class\n"\
> create_pvc.yaml

echo \
"\n\
apiVersion: v1\n\
kind: Pod\n\
metadata:\n\
  name: datatransfer-pod\n\
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
      claimName: my-disk-claim\n"\
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

    # Assume that the environment variable BOQ_BUCKET has been set.
    echo;echo BOQ_BUCKET=${BOQ_BUCKET}

    echo;echo Executing: gsutil ls ${BOQ_BUCKET}/TrainingData_Geojson
    gsutil ls ${BOQ_BUCKET}/TrainingData_Geojson

    echo;echo Executing: mkdir datatransfer
    mkdir datatransfer

    echo;echo Executing: gsutil -m cp -r ${BOQ_BUCKET}/TrainingData_Geojson datatransfer
    gsutil -m cp -r ${BOQ_BUCKET}/TrainingData_Geojson datatransfer

    echo;echo Executing: sudo kubectl cp datatransfer/TrainingData_Geojson default/datatransfer-pod:/datatransfer
    sudo kubectl cp datatransfer/TrainingData_Geojson default/datatransfer-pod:/datatransfer

    # echo;echo Executing: gsutil -m cp -r ${BOQ_BUCKET}/img datatransfer
    # gsutil -m cp -r ${BOQ_BUCKET}/img datatransfer

    # echo;echo Executing: sudo kubectl cp datatransfer/img default/datatransfer-pod:/datatransfer
    # sudo kubectl cp datatransfer/img default/datatransfer-pod:/datatransfer

    echo;echo Executing: ls -l datatransfer
    ls -l datatransfer

    echo;echo Executing: ls -l datatransfer/*
    ls -l datatransfer/*

    # echo;echo Executing: ls -l datatransfer/TrainingData_Geojson
    # ls -l datatransfer/TrainingData_Geojson

    # echo;echo Executing: ls -l datatransfer/img
    # ls -l datatransfer/img

    # echo;echo Executing: sudo kubectl exec -n default datatransfer-pod -- /bin/sh -c 'mkdir /datatransfer/input/; mkdir /datatransfer/output/; ls -l /datatransfer; exit'
    # sudo kubectl exec -n default datatransfer-pod -- /bin/sh -c 'mkdir /datatransfer/input/; mkdir /datatransfer/output/; ls -l /datatransfer; exit'

    # echo;echo Executing: kubectl exec -n default datatransfer-pod -- /bin/sh -c 'gsutil cp -r ${EXTERNAL_BUCKET}/input /datatransfer/input; ls -l /datatransfer/input; exit'
    # sudo kubectl exec -n default datatransfer-pod -- /bin/sh -c 'kubectl cp ${EXTERNAL_BUCKET}/input /datatransfer/input; ls -l /datatransfer/input; exit'

    # echo;echo Executing: ls -l default/datatransfer-pod:/datatransfer
    # ls -l default/datatransfer-pod:/datatransfer

    # echo;echo Executing: gsutil cp -r ${EXTERNAL_BUCKET}/input default/datatransfer-pod:/datatransfer/input
    # gsutil cp -r ${EXTERNAL_BUCKET}/input default/datatransfer-pod:/datatransfer/input
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

    sleep 60

    echo;echo Executing: sudo kubectl get nodes
    sudo kubectl get nodes

    echo;echo Executing: sudo kubectl get pods -o wide
    sudo kubectl get pods -o wide

    echo;echo Executing: sudo kubectl delete pod datatransfer-pod
    sudo kubectl delete pod datatransfer-pod
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
  name: my-disk-claim\n\
  namespace: default\n\
spec:\n\
  resources:\n\
    requests:\n\
      storage: 500Gi\n\
  accessModes:\n\
    - ReadWriteOnce\n\
  storageClassName: my-storage-class\n"\
> create_pvc.yaml

echo \
"\n\
apiVersion: v1\n\
kind: Pod\n\
metadata:\n\
  name: datatransfer-pod\n\
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
      claimName: my-disk-claim\n"\
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

    echo;echo Executing: sudo kubectl cp default/datatransfer-pod:/datatransfer/output datatransfer/output
    sudo kubectl cp default/datatransfer-pod:/datatransfer/output datatransfer/output
    sleep 10

    echo;echo Executing: ls -l datatransfer
    ls -l datatransfer
    sleep 10

    echo;echo Executing: ls -l datatransfer/output
    ls -l datatransfer/output
    sleep 10

    # Assume that the environment variable EXTERNAL_BUCKET has been set.
    echo;echo Executing: gsutil -m cp -r datatransfer/output ${EXTERNAL_BUCKET}
    gsutil -m cp -r datatransfer/output ${EXTERNAL_BUCKET}
    sleep 10

    echo;echo Executing: gsutil ls ${EXTERNAL_BUCKET}
    gsutil ls ${EXTERNAL_BUCKET}
    sleep 10

    echo;echo Executing: gsutil ls ${EXTERNAL_BUCKET}/output
    gsutil ls ${EXTERNAL_BUCKET}/output
    sleep 10

    echo;echo Executing: sudo kubectl delete pod datatransfer-pod
    sudo kubectl delete pod datatransfer-pod

    echo;echo Executing: sudo kubectl get nodes
    sudo kubectl get nodes
    sleep 10

    echo;echo Executing: sudo kubectl get pods -o wide
    sudo kubectl get pods -o wide
    sleep 10
    """

    # Tasks definitions
    create_node_pool_task = BashOperator(
        task_id="create_node_pool",
        bash_command=create_node_pool_command,
        xcom_push=True,
        dag=dag
    )

    delete_node_pool_task = BashOperator(
        task_id="delete_node_pool",
        bash_command=delete_node_pools_command,
        trigger_rule='all_done', # Always run even if failures so the node pool is deleted
        # xcom_push=True,
        dag=dag
    )

    injest_input_data_task = BashOperator(
        task_id="injest_input_data",
        bash_command=injest_input_data_command,
        xcom_push=True,
        dag=dag
    )

    delete_datatransfer_pod = BashOperator(
        task_id="delete_datatransfer_pod",
        bash_command=delete_datatransfer_pod_command,
        xcom_push=True,
        dag=dag
    )

    persist_output_data_task = BashOperator(
        task_id="persist_output_data",
        bash_command=persist_output_data_command,
        xcom_push=True,
        dag=dag
    )

    sum_task_0 = kubernetes_pod.KubernetesPodOperator(
        task_id='sum_task_0',
        name='etl',
        namespace='default',
        startup_timeout_seconds=86400,
      # image='gcr.io/gcp-runtimes/ubuntu_18_0_4',
      # image='paradisepilot/miniconda3-r-base:0.1',
        image='paradisepilot/fpca-base:0.8',
      # cmds=["sh", "-c", 'R -e "DF.temp <- utils::read.csv(\'/home/airflow/gcs/data/input/input-file-00.csv\'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists(\'/home/airflow/gcs/data/output\')) {base::dir.create(\'/home/airflow/gcs/data/output\',recursive=TRUE)}; write.csv(x = DF.results, file = \'/home/airflow/gcs/data/output/output-00.csv\', row.names = FALSE)"'],
      # cmds=["/opt/conda/bin/Rscript", "-e", "DF.temp <- utils::read.csv('/home/airflow/gcs/data/input/input-file-00.csv'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists('/home/airflow/gcs/data/output')) {base::dir.create('/home/airflow/gcs/data/output',recursive=TRUE)}; write.csv(x = DF.results, file = '/home/airflow/gcs/data/output/output-00.csv', row.names = FALSE)"],
      # cmds=["sh", "-c", "echo;echo \'Sleeping ...\' ; sleep 10 ; echo;echo whoami=`whoami` ; echo;echo ls -l /usr/local/bin ; ls -l /usr/local/bin ; echo;echo ls -l /data ; ls -l /data ; echo;echo ls -l /opt/conda/bin ; ls -l /opt/conda/bin/ ; echo;echo \'Done\'"],
      # cmds=["sh", "-c", "echo;echo \'Sleeping ...\' ; sleep 10 ; echo;echo whoami=`whoami` ; echo;echo ls -l /usr/local/bin ; ls -l /usr/local/bin ; echo;echo EXTERNAL_BUCKET=${EXTERNAL_BUCKET}; echo;echo SERVICE_ACCOUNT_KEY_JSON=${SERVICE_ACCOUNT_KEY_JSON}; echo;echo ls -l ${SERVICE_ACCOUNT_KEY_JSON}; ls -l ${SERVICE_ACCOUNT_KEY_JSON}; echo;echo ls -l /opt/conda/bin ; ls -l /opt/conda/bin/ ; echo;echo ls -l /datatransfer/input; ls -l /datatransfer/input/ ; echo;echo \'Done\'"],
      # cmds=["sh", "-c", "echo;echo \'Sleeping ...\' ; sleep 10 ; echo;echo whoami=`whoami` ; echo;echo ls -l /usr/local/bin ; ls -l /usr/local/bin ; echo;echo EXTERNAL_BUCKET=${EXTERNAL_BUCKET}; echo;echo ls -l /opt/conda/bin ; ls -l /opt/conda/bin/ ; echo;echo ls -l /datatransfer/input; ls -l /datatransfer/input/ ; echo;echo \'Done\'"],
        cmds=["sh", "-c", "echo;echo \'Sleeping ...\' ; sleep 10 ; echo;echo whoami=`whoami` ; echo;echo ls -l /usr/local/bin ; ls -l /usr/local/bin ; echo;echo BOQ_BUCKET=${BOQ_BUCKET}; echo;echo ls -l /opt/conda/bin ; ls -l /opt/conda/bin/ ; echo;echo \'Done\'"],
      # volumes=["/home/airflow/gcs/data:/data"],

      # volumes=[volume],
      # volume_mounts=[volume_mount],
      # resources={'request_cpu': "15000m", 'request_memory': "61440M"},
      # resources={'request_cpu':  "9000m", 'request_memory':  "3072M"},
        resources={'request_cpu':  "3000m", 'request_memory':  "3072M"},

      # secrets=[secret_envvar_external_bucket,secret_volume_service_account_key],
      # secrets=[secret_envvar_external_bucket],
        # env_vars={
        #     'SERVICE_ACCOUNT_KEY_JSON': '/var/secrets/google/service-account-key.json'
        #     },
      # is_delete_operator_pod=True,
        tolerations=[{
            'key': "work",
            'operator': 'Equal',
            'value': 'well',
            'effect': "NoSchedule"
            }],
        # affinity allows you to constrain which nodes your pod is eligible to
        # be scheduled on, based on labels on the node. In this case, if the
        # label 'cloud.google.com/gke-nodepool' with value
        # 'nodepool-label-value' or 'nodepool-label-value2' is not found on any
        # nodes, it will fail to schedule.
        affinity={
            'nodeAffinity': {
                # requiredDuringSchedulingIgnoredDuringExecution means in order
                # for a pod to be scheduled on a node, the node must have the
                # specified labels. However, if labels on a node change at
                # runtime such that the affinity rules on a pod are no longer
                # met, the pod will still continue to run on the node.
                'requiredDuringSchedulingIgnoredDuringExecution': {
                    'nodeSelectorTerms': [{
                        'matchExpressions': [{
                            # When nodepools are created in Google Kubernetes
                            # Engine, the nodes inside of that nodepool are
                            # automatically assigned the label
                            # 'cloud.google.com/gke-nodepool' with the value of
                            # the nodepool's name.
                            'key': 'cloud.google.com/gke-nodepool',
                            'operator': 'In',
                            # The label key's value that pods can be scheduled
                            # on.
                            # In this case it will execute the command on the node
                            # pool created by the Airflow bash operator.
                            'values': [
                                Variable.get("node_pool", default_var=node_pool_value)
                            ]
                        }]
                    }]
                }
            }
        })

    sum_task_1 = kubernetes_pod.KubernetesPodOperator(
        task_id='sum_task_1',
        name='etl',
        namespace='default',
      # image='gcr.io/gcp-runtimes/ubuntu_18_0_4',
      # image='paradisepilot/miniconda3-r-base:0.1',
        image='paradisepilot/fpca-base:0.8',
      # cmds=["sh", "-c", 'R -e "DF.temp <- utils::read.csv(\'/home/airflow/gcs/data/input/input-file-01.csv\'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists(\'/home/airflow/gcs/data/output\')) {base::dir.create(\'/home/airflow/gcs/data/output\',recursive=TRUE)}; write.csv(x = DF.results, file = \'/home/airflow/gcs/data/output/output-01.csv\', row.names = FALSE)"'],
      # cmds=["/opt/conda/bin/Rscript", "-e", "DF.temp <- utils::read.csv('/home/airflow/gcs/data/input/input-file-01.csv'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists('/home/airflow/gcs/data/output')) {base::dir.create('/home/airflow/gcs/data/output',recursive=TRUE)}; write.csv(x = DF.results, file = '/home/airflow/gcs/data/output/output-01.csv', row.names = FALSE)"],
      # cmds=["sh", "-c", 'echo \'Sleeping ...\'; sleep 10; echo;echo ls -l /home/airflow/gcs/data/ ; ls -l /home/airflow/gcs/data/ ; echo;echo ls -l /datatransfer/input; ls -l /datatransfer/input/ ; echo;echo \'Done!\''],
        cmds=["sh", "-c", 'echo "Sleeping ..."; sleep 10; echo;echo ls -l /home/airflow/gcs/data/ ; ls -l /home/airflow/gcs/data/ ; echo;echo ls -l /datatransfer/TrainingData_Geojson; ls -l /datatransfer/TrainingData_Geojson/ ; echo;echo mkdir github ; mkdir github ; echo;echo cd github ; cd github ; echo;echo git clone https://github.com/STC-NWRC/bay-of-quinte.git ; git clone https://github.com/STC-NWRC/bay-of-quinte.git ; echo;echo cd bay-of-quinte ; cd bay-of-quinte ; echo;echo chmod ugo+x run-main.sh ; chmod ugo+x run-main.sh ;  echo;echo ./run-main.sh apple ; ./run-main.sh apple ; echo;echo pwd ; pwd ; echo;echo "ls -l .." ; ls -l .. ; echo;echo "ls -l ../.." ; ls -l ../.. ; echo;echo "tree ../.." ; tree ../.. ; echo;echo "cat ../../gittmp/bay-of-quinte/output-apple/stdout.R.main" ; cat ../../gittmp/bay-of-quinte/output-apple/stdout.R.main ; echo;echo "cd ../.." ; cd ../.. ; echo;echo pwd ; pwd ; echo;echo ls -l ; ls -l ; mkdir /datatransfer/output ; echo;echo rm -rf /datatransfer/output/output-apple; rm -rf /datatransfer/output/output-apple ; echo;echo cp -r gittmp/bay-of-quinte/output-apple /datatransfer/output/output-apple ; cp -r gittmp/bay-of-quinte/output-apple /datatransfer/output/output-apple ; echo;echo "ls -l /datatransfer/output/" ; ls -l /datatransfer/output/ ; echo;echo "ls -l /datatransfer/output/output-apple" ; ls -l /datatransfer/output/output-apple ; echo;echo \'Done!\''],
        startup_timeout_seconds=86400,
      # is_delete_operator_pod=True,

        volumes=[volume],
        volume_mounts=[volume_mount],
      # resources={'request_cpu': "15000m", 'request_memory': "61440M"},
        resources={'request_cpu':  "3000m", 'request_memory':  "3072M"},

      # secrets=[secret_envvar_external_bucket,secret_volume_service_account_key],
      # secrets=[secret_envvar_external_bucket],
        # env_vars={
        #     'SERVICE_ACCOUNT_KEY_JSON': '/var/secrets/google/service-account-key.json'
        #     },
      # is_delete_operator_pod=True,
        tolerations=[{
            'key': "work",
            'operator': 'Equal',
            'value': 'well',
            'effect': "NoSchedule"
            }],
        # affinity allows you to constrain which nodes your pod is eligible to
        # be scheduled on, based on labels on the node. In this case, if the
        # label 'cloud.google.com/gke-nodepool' with value
        # 'nodepool-label-value' or 'nodepool-label-value2' is not found on any
        # nodes, it will fail to schedule.
        affinity={
            'nodeAffinity': {
                # requiredDuringSchedulingIgnoredDuringExecution means in order
                # for a pod to be scheduled on a node, the node must have the
                # specified labels. However, if labels on a node change at
                # runtime such that the affinity rules on a pod are no longer
                # met, the pod will still continue to run on the node.
                'requiredDuringSchedulingIgnoredDuringExecution': {
                    'nodeSelectorTerms': [{
                        'matchExpressions': [{
                            # When nodepools are created in Google Kubernetes
                            # Engine, the nodes inside of that nodepool are
                            # automatically assigned the label
                            # 'cloud.google.com/gke-nodepool' with the value of
                            # the nodepool's name.
                            'key': 'cloud.google.com/gke-nodepool',
                            'operator': 'In',
                            # The label key's value that pods can be scheduled
                            # on.
                            # In this case it will execute the command on the node
                            # pool created by the Airflow bash operator.
                            'values': [
                                Variable.get("node_pool", default_var=node_pool_value)
                            ]
                        }]
                    }]
                }
            }
        })

    sum_task_2 = kubernetes_pod.KubernetesPodOperator(
        task_id='sum_task_2',
        name='etl',
        namespace='default',
      # image='gcr.io/gcp-runtimes/ubuntu_18_0_4',
      # image='paradisepilot/miniconda3-r-base:0.1',
        image='paradisepilot/fpca-base:0.8',
      # cmds=["sh", "-c", 'R -e "DF.temp <- utils::read.csv(\'/home/airflow/gcs/data/input/input-file-02.csv\'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists(\'/home/airflow/gcs/data/output\')) {base::dir.create(\'/home/airflow/gcs/data/output\',recursive=TRUE)}; write.csv(x = DF.results, file = \'/home/airflow/gcs/data/output/output-02.csv\', row.names = FALSE)"'],
      # cmds=["/opt/conda/bin/Rscript", "-e", "DF.temp <- utils::read.csv('/home/airflow/gcs/data/input/input-file-02.csv'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists('/home/airflow/gcs/data/output')) {base::dir.create('/home/airflow/gcs/data/output',recursive=TRUE)}; write.csv(x = DF.results, file = '/home/airflow/gcs/data/output/output-02.csv', row.names = FALSE)"],
      # cmds=["sh", "-c", 'echo \'Sleeping ...\'; sleep 10; echo;echo which docker ; which docker; echo;echo which R ; which R ; echo;echo R -e "library(help=arrow)" ; R -e "library(help=arrow)"; echo;echo R -e "library(help=fpcFeatures)" ; R -e "library(help=fpcFeatures)"; echo;echo ls -l /home/airflow/gcs/data/ ; ls -l /home/airflow/gcs/data/ ; echo;echo ls -l /datatransfer/input ; ls -l /datatransfer/input/ ; echo;echo \'Done!\''],
        cmds=["sh", "-c", 'echo \'Sleeping ...\'; sleep 10; echo;echo which docker ; which docker; echo;echo which R ; which R ; echo;echo R -e "library(help=arrow)" ; R -e "library(help=arrow)"; echo;echo R -e "library(help=fpcFeatures)" ; R -e "library(help=fpcFeatures)"; echo;echo ls -l /home/airflow/gcs/data/ ; ls -l /home/airflow/gcs/data/ ; echo;echo ls -l /datatransfer/TrainingData_Geojson ; ls -l /datatransfer/TrainingData_Geojson/ ; echo;echo mkdir github ; mkdir github ; echo;echo cd github ; cd github ; echo;echo git clone https://github.com/STC-NWRC/bay-of-quinte.git ; git clone https://github.com/STC-NWRC/bay-of-quinte.git ; echo;echo cd bay-of-quinte ; cd bay-of-quinte ; echo;echo chmod ugo+x run-main.sh ; chmod ugo+x run-main.sh ;  echo;echo ./run-main.sh orange ; ./run-main.sh orange ; echo;echo pwd ; pwd ; echo;echo "ls -l .." ; ls -l .. ; echo;echo "ls -l ../.." ; ls -l ../.. ; echo;echo "tree ../.." ; tree ../.. ; echo;echo "cat ../../gittmp/bay-of-quinte/output-orange/stdout.R.main" ; cat ../../gittmp/bay-of-quinte/output-orange/stdout.R.main ; echo;echo "cd ../.." ; cd ../.. ; echo;echo pwd ; pwd ; echo;echo ls -l ; ls -l ; mkdir /datatransfer/output ; echo;echo rm -rf /datatransfer/output/output-orange; rm -rf /datatransfer/output/output-orange ; echo;echo cp -r gittmp/bay-of-quinte/output-orange /datatransfer/output/output-orange ; cp -r gittmp/bay-of-quinte/output-orange /datatransfer/output/output-orange ; echo;echo "ls -l /datatransfer/output/" ; ls -l /datatransfer/output/ ; echo;echo "ls -l /datatransfer/output/output-orange" ; ls -l /datatransfer/output/output-orange ; echo;echo \'Done!\''],
        startup_timeout_seconds=86400,
      # is_delete_operator_pod=True,

        volumes=[volume],
        volume_mounts=[volume_mount],
      # resources={'request_cpu': "15000m", 'request_memory': "61440M"},
        resources={'request_cpu':  "3000m", 'request_memory':  "3072M"},

      # secrets=[secret_envvar_external_bucket,secret_volume_service_account_key],
      # secrets=[secret_envvar_external_bucket],
        # env_vars={
        #     'SERVICE_ACCOUNT_KEY_JSON': '/var/secrets/google/service-account-key.json'
        #     },
      # is_delete_operator_pod=True,
        tolerations=[{
            'key': "work",
            'operator': 'Equal',
            'value': 'well',
            'effect': "NoSchedule"
            }],
        # affinity allows you to constrain which nodes your pod is eligible to
        # be scheduled on, based on labels on the node. In this case, if the
        # label 'cloud.google.com/gke-nodepool' with value
        # 'nodepool-label-value' or 'nodepool-label-value2' is not found on any
        # nodes, it will fail to schedule.
        affinity={
            'nodeAffinity': {
                # requiredDuringSchedulingIgnoredDuringExecution means in order
                # for a pod to be scheduled on a node, the node must have the
                # specified labels. However, if labels on a node change at
                # runtime such that the affinity rules on a pod are no longer
                # met, the pod will still continue to run on the node.
                'requiredDuringSchedulingIgnoredDuringExecution': {
                    'nodeSelectorTerms': [{
                        'matchExpressions': [{
                            # When nodepools are created in Google Kubernetes
                            # Engine, the nodes inside of that nodepool are
                            # automatically assigned the label
                            # 'cloud.google.com/gke-nodepool' with the value of
                            # the nodepool's name.
                            'key': 'cloud.google.com/gke-nodepool',
                            'operator': 'In',
                            # The label key's value that pods can be scheduled
                            # on.
                            # In this case it will execute the command on the node
                            # pool created by the Airflow bash operator.
                            'values': [
                                Variable.get("node_pool", default_var=node_pool_value)
                            ]
                        }]
                    }]
                }
            }
        })

    # Tasks order
    # create_node_pool_task >> injest_input_data_task
    # create_node_pool_task >> injest_input_data_task >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task
    # create_node_pool_task >> injest_input_data_task >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task >> delete_node_pool_task
    # create_node_pool_task >> injest_input_data_task >> delete_datatransfer_pod >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task >> delete_node_pool_task
    # create_node_pool_task >> injest_input_data_task >> delete_datatransfer_pod >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task >> delete_node_pool_task
    injest_input_data_task >> delete_datatransfer_pod >> create_node_pool_task >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task >> delete_node_pool_task
