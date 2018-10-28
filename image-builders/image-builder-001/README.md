
How to launch a Google Cloud VM instance, and install some tools on it using these scripts:
===========================================================================================

 *  At the Google cloudshell prompt, clone the following GitHub project:
 ~~~
$ git clone https://github.com/paradisepilot/gcp
$ cd gcp/image-builders/image-builder-001
 ~~~

 *  In order to launch a VM instance, execute the following:
~~~
$ ./gcloud-compute-instances-create.sh
~~~

 *  Once the VM instance is running, execute the following in order to log on to it:
~~~
$ ./gcloud-compute-ssh.sh
~~~

