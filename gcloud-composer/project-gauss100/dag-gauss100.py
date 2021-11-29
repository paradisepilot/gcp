import datetime

from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.models import Variable
from airflow.kubernetes.secret import Secret

import os

JOB_NAME = 'gauss100_gke'
start_date = datetime.datetime(2021, 1, 31)

default_args = {
    'start_date': start_date,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=1),
}

secret_envvar_external_bucket = Secret(
    # Name of the Kubernetes Secret
    secret='airflow-secrets-fpca',
    # Expose the secret as environment variable.
    deploy_type='env',
    # Key of a secret stored in this Secret object
    key='external_bucket',
    # The name of the environment variable, since deploy_type is `env` rather than `volume`.
    deploy_target='EXTERNAL_BUCKET'
    )

secret_volume_service_account_key = Secret(
    # Name of Kubernetes Secret
    secret='airflow-secrets-fpca',
    # type of secret
    deploy_type='volume',
    # Key in the form of service account file name
    key='service-account-key.json',
    # Path where we mount the secret as volume
    deploy_target='/var/secrets/google'
    )

with models.DAG(JOB_NAME,
                default_args=default_args,
                schedule_interval=None,
                catchup=False) as dag:

    # This value can be customized to whatever format is preferred for the node pool name
    # Default node pool naming format is <cluster name>-node-pool-<execution_date>
    # node_pool_value = "$COMPOSER_ENVIRONMENT-node-pool-$(echo {{ ts_nodash }} | awk '{print tolower($0)}')"
    node_pool_value = "ndpl-$(echo {{ ts_nodash }} | awk '{print tolower($0)}')"

    create_node_pool_command = """
    # Set some environment variables in case they were not set already
    [ -z "${NODE_COUNT}" ] && NODE_COUNT=3
    [ -z "${MACHINE_TYPE}" ] && MACHINE_TYPE=n1-standard-2
    [ -z "${SCOPES}" ] && SCOPES=default,cloud-platform
    [ -z "${NODE_DISK_SIZE}" ] && NODE_DISK_SIZE=20

    # Generate node-pool name
    NODE_POOL=""" + node_pool_value + """

    echo;echo COMPOSER_GKE_ZONE=${COMPOSER_GKE_ZONE}

    echo;echo COMPOSER_GKE_NAME=${COMPOSER_GKE_NAME}

    echo;echo NODE_POOL=${NODE_POOL}

    echo;echo MACHINE_TYPE=${MACHINE_TYPE}

    echo;echo NODE_COUNT=${NODE_COUNT}

    echo;echo NODE_DISK_SIZE=${NODE_DISK_SIZE}

    echo;echo SCOPES=${SCOPES}

    ### It is important to set container/cluster; otherwise, Composer would
    ### throw an error at the node pool creation command below
    ### due to the fact that the node pool creation would require more vCPU
    ### than regional vCPU quota.
    echo;echo >> gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    ### set kubectl credentials (required by subsequent commands)
    ### Use the gcloud composer command to connect the kubectl command to the cluster.
    ### https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies#viewing_installed_python_packages
    echo;echo > gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}
    gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${ZONE}

    echo;echo >> gcloud container node-pools create ...
    gcloud container node-pools create ${NODE_POOL} \
        --project=${GCP_PROJECT}       --cluster=${COMPOSER_GKE_NAME} --zone=${COMPOSER_GKE_ZONE} \
        --machine-type=${MACHINE_TYPE} --num-nodes=${NODE_COUNT}      --disk-size=${NODE_DISK_SIZE} \
        --scopes=${SCOPES} \
        --enable-autoupgrade

    ### Set the airflow variable name
    echo;echo > airflow variables -s node_pool ${NODE_POOL}
    airflow variables -s node_pool ${NODE_POOL}

    ### create Kubernetes secret environment variable for EXTERNAL_BUCKET, and
    ### create Kubernetes secret volume for service account key
    gsutil cp ${EXTERNAL_BUCKET}/secrets/service-account-key.json .
    sleep 5
    echo;echo >> ls -l service-account-key.json
    ls -l service-account-key.json
    echo;echo >> kubectl create secret generic airflow-secrets-fpca ...
    kubectl create secret generic airflow-secrets-fpca \
        --from-literal=external_bucket=${EXTERNAL_BUCKET} \
        --from-file=service-account-key.json
    sleep 5
    # rm -f service-account-key.json

    ### check Kubernetes secrets
    echo;echo >> kubectl get secrets
    kubectl get secrets
    """

    delete_node_pools_command = """
    # Generate node-pool name
    NODE_POOL=""" + node_pool_value + """

    echo; echo >> gcloud config set container/cluster ${COMPOSER_GKE_NAME}
    gcloud config set container/cluster ${COMPOSER_GKE_NAME}

    echo;echo >> gcloud container node-pools delete ${NODE_POOL} --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet
    gcloud container node-pools delete ${NODE_POOL} --zone ${COMPOSER_GKE_ZONE} --cluster ${COMPOSER_GKE_NAME} --quiet
    """

    injest_input_data_command = """
    # Assume that the environment variable EXTERNAL_BUCKET has been set.
    echo;echo EXTERNAL_BUCKET=${EXTERNAL_BUCKET}

    echo;echo >> gsutil ls ${EXTERNAL_BUCKET}/input/
    gsutil ls ${EXTERNAL_BUCKET}/input/

    echo;echo >> gsutil cp -r ${EXTERNAL_BUCKET}/input /home/airflow/gcs/data
    gsutil cp -r ${EXTERNAL_BUCKET}/input /home/airflow/gcs/data
    """

    persist_output_data_command = """
    # Assume that the environment variable EXTERNAL_BUCKET has been set.
    # echo;echo >> gsutil cp -r /home/airflow/gcs/data/output ${EXTERNAL_BUCKET}/output
    # gsutil cp -r /home/airflow/gcs/data/output ${EXTERNAL_BUCKET}/output
    echo
    echo Doing nothing.
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
        trigger_rule='all_done',        # Always run even if failures so the node pool is deleted
        dag=dag
    )

    injest_input_data_task = BashOperator(
        task_id="injest_input_data",
        bash_command=injest_input_data_command,
      # xcom_push=True,
        dag=dag
    )

    persist_output_data_task = BashOperator(
        task_id="persist_output_data",
        bash_command=persist_output_data_command,
      # xcom_push=True,
        dag=dag
    )

    sum_task_0 = kubernetes_pod.KubernetesPodOperator(
        task_id='sum_task_0',
        name='etl',
        namespace='default',
        startup_timeout_seconds=720,
      # image='gcr.io/gcp-runtimes/ubuntu_18_0_4',
      # image='paradisepilot/miniconda3-r-base:0.1',
        image='paradisepilot/fpca-base:0.7',
      # cmds=["sh", "-c", 'R -e "DF.temp <- utils::read.csv(\'/home/airflow/gcs/data/input/input-file-00.csv\'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists(\'/home/airflow/gcs/data/output\')) {base::dir.create(\'/home/airflow/gcs/data/output\',recursive=TRUE)}; write.csv(x = DF.results, file = \'/home/airflow/gcs/data/output/output-00.csv\', row.names = FALSE)"'],
      # cmds=["/opt/conda/bin/Rscript", "-e", "DF.temp <- utils::read.csv('/home/airflow/gcs/data/input/input-file-00.csv'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists('/home/airflow/gcs/data/output')) {base::dir.create('/home/airflow/gcs/data/output',recursive=TRUE)}; write.csv(x = DF.results, file = '/home/airflow/gcs/data/output/output-00.csv', row.names = FALSE)"],
      # cmds=["sh", "-c", "echo;echo \'Sleeping ...\' ; sleep 10 ; echo;echo whoami=`whoami` ; echo;echo ls -l /usr/local/bin ; ls -l /usr/local/bin ; echo;echo ls -l /data ; ls -l /data ; echo;echo ls -l /opt/conda/bin ; ls -l /opt/conda/bin/ ; echo;echo \'Done\'"],
        cmds=["sh", "-c", "echo;echo \'Sleeping ...\' ; sleep 10 ; echo;echo whoami=`whoami` ; echo;echo ls -l /usr/local/bin ; ls -l /usr/local/bin ; echo;echo EXTERNAL_BUCKET=${EXTERNAL_BUCKET}; echo;echo SERVICE_ACCOUNT_KEY_JSON=${SERVICE_ACCOUNT_KEY_JSON}; echo;echo ls -l ${SERVICE_ACCOUNT_KEY_JSON}; ls -l ${SERVICE_ACCOUNT_KEY_JSON}; echo;echo ls -l /opt/conda/bin ; ls -l /opt/conda/bin/ ; echo;echo \'Done\'"],
      # volumes=["/home/airflow/gcs/data:/data"],
        secrets=[secret_envvar_external_bucket,secret_volume_service_account_key],
        env_vars={
            'SERVICE_ACCOUNT_KEY_JSON': '/var/secrets/google/service-account-key.json'
            },
      # is_delete_operator_pod=True,
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
        image='paradisepilot/fpca-base:0.7',
        cmds=["sh", "-c", 'echo \'Sleeping ...\'; sleep 10; ls -l /home/airflow/gcs/data/; echo \'Done!\''],
      # cmds=["sh", "-c", 'R -e "DF.temp <- utils::read.csv(\'/home/airflow/gcs/data/input/input-file-01.csv\'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists(\'/home/airflow/gcs/data/output\')) {base::dir.create(\'/home/airflow/gcs/data/output\',recursive=TRUE)}; write.csv(x = DF.results, file = \'/home/airflow/gcs/data/output/output-01.csv\', row.names = FALSE)"'],
      # cmds=["/opt/conda/bin/Rscript", "-e", "DF.temp <- utils::read.csv('/home/airflow/gcs/data/input/input-file-01.csv'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists('/home/airflow/gcs/data/output')) {base::dir.create('/home/airflow/gcs/data/output',recursive=TRUE)}; write.csv(x = DF.results, file = '/home/airflow/gcs/data/output/output-01.csv', row.names = FALSE)"],
        startup_timeout_seconds=720,
      # is_delete_operator_pod=True,
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
        image='paradisepilot/fpca-base:0.7',
        cmds=["sh", "-c", 'echo \'Sleeping ...\'; sleep 10; which docker; which R; R -e "library(help=arrow)"; R -e "library(help=fpcFeatures)"; echo \'Done!\''],
      # cmds=["sh", "-c", 'R -e "DF.temp <- utils::read.csv(\'/home/airflow/gcs/data/input/input-file-02.csv\'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists(\'/home/airflow/gcs/data/output\')) {base::dir.create(\'/home/airflow/gcs/data/output\',recursive=TRUE)}; write.csv(x = DF.results, file = \'/home/airflow/gcs/data/output/output-02.csv\', row.names = FALSE)"'],
      # cmds=["/opt/conda/bin/Rscript", "-e", "DF.temp <- utils::read.csv('/home/airflow/gcs/data/input/input-file-02.csv'); DF.results <- sum(DF.temp[,1]); if (\!dir.exists('/home/airflow/gcs/data/output')) {base::dir.create('/home/airflow/gcs/data/output',recursive=TRUE)}; write.csv(x = DF.results, file = '/home/airflow/gcs/data/output/output-02.csv', row.names = FALSE)"],
        startup_timeout_seconds=720,
      # is_delete_operator_pod=True,
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
    create_node_pool_task >> injest_input_data_task >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task >> delete_node_pool_task
    # create_node_pool_task >> injest_input_data_task >> [sum_task_0, sum_task_1, sum_task_2] >> persist_output_data_task
