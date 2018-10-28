
How to launch a Google Cloud Engine (GCE) instance, and install certain software tools on it using these scripts:
=================================================================================================================

 *  At the Google cloudshell prompt, clone the following GitHub project:
 ~~~
$ git clone https://github.com/paradisepilot/gcp
$ cd gcp/image-builders/image-builder-001
 ~~~

 *  In order to launch a GCE instance, execute the following:
~~~
$ ./gcloud-compute-instances-create.sh
~~~

 *  Once the GCE instance is running, execute the following in order to log on to it:
~~~
$ ./gcloud-compute-ssh.sh
~~~

 *  At the shell prompt of the running GCE instance, execute the following in order to install the software tools:
~~~
paradisepilot@voyager:~/gcp/image-builders/image-builder-001$ ./image-builder-001.sh > stdout.sh.image-builder-001 2> stderr.sh.image-builder-001
~~~
