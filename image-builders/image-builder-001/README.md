
How to create a Google Cloud Engine (GCE) instance, and install certain software tools on it using these scripts:
=================================================================================================================

 *  At the Google cloudshell prompt, clone the following GitHub project:
 ~~~
paradisepilot@cloudshell:~ (alert-basis-204816)$ git clone https://github.com/paradisepilot/gcp
 ~~~

 *  Change directory (cd) as follows:
 ~~~
paradisepilot@cloudshell:~ (alert-basis-204816)$ cd gcp/image-builders/image-builder-001/
 ~~~

 *  Execute the following in order to create a new GCE instance:
~~~
paradisepilot@cloudshell:~/gcp/image-builders/image-builder-001 (alert-basis-204816)$ ./gcloud-compute-instances-create.sh
~~~

 *  Once the GCE instance is running, execute the following in order to log on to it:
~~~
paradisepilot@cloudshell:~/gcp/image-builders/image-builder-001 (alert-basis-204816)$ ./gcloud-compute-ssh.sh
~~~

 *  At the shell prompt of the running GCE instance, execute the following in order to install the software tools (this will take several minutes):
~~~
paradisepilot@voyager:~/gcp/image-builders/image-builder-001$ ./image-builder-001.sh > stdout.sh.image-builder-001 2> stderr.sh.image-builder-001
~~~

 *  In order to test the freshly installed Python and the modules we just installed, launch Python in the GCE instance:
~~~
paradisepilot@voyager:~/gcp/image-builders/image-builder-001$ cd ~/miniconda/bin/
paradisepilot@voyager:~/miniconda/bin$ ./python3
~~~

 *  At the Python prompt, import the following Python modules:
 ~~~
 >>> import matplotlib, seaborn, h5py, pandas, sklearn, gensim, pydot_ng, tensorflow, keras
 ~~~

 *  Do NOT forget to delete (or, at least stop) the instance once you are done:
 ~~~
paradisepilot@voyager:~/miniconda/bin$ cd ~/gcp/image-builders/image-builder-001/
paradisepilot@voyager:~/gcp/image-builders/image-builder-001$ ./gcloud-compute-instances-delete.sh
 ~~~
