# Collections Plugins Directory
This directory can be used to ship various plugins inside an Ansible collection. Each plugin is placed in a folder that
is named after the type of plugin it is in. It can also include the `module_utils` and `modules` directory that
would contain module utils and modules respectively.

Plugins included in this Ansible collection are listed below:

```
└── plugins
    ├── install_openshift_on_aws
```

## install_openshift_on_aws
This module automates installatio of Openshift Container Platform clusters on AWS

### Pre-requisites
AWS Credentials need to be set in environment. 

```sh
export AWS_ACCESS_KEY_ID='{replace}'
export AWS_SECRET_ACCESS_KEY='{replace}'
```

***note: if you are internal Red Hat or Partner you can order AWS open environments at demo.redhat.com***

Create ansible vault using command below

```sh
ansible-vault create vars/secrets.yml
```

Inlcude information below 

```yaml
pull_secret: '' # optional you can dowload pull secret from cloud.redhat.com openshift/downloads
rh_offline_token: '' # optional, this is only used to automatically download pull secret from openshift downloads at console.redhat.com
```

Set the vault secret in environment variable as shown below

```sh
export VAULT_SECRET='{replace}'
```

### Using the module
* Install this collection by running the command below

```sh
 ansible-galaxy collection install rprakashg.openshift_automation --upgrade 
```

Create a playbook and include below snippet

```yaml
---
- name: Install hub cluster on AWS
  hosts: localhost
  tasks:
    - name: install cluster
      rprakashg.openshift_automation.install_openshift_on_aws:
        cluster_name: hub
        region: us-west-2
        base_domain: ocp.example.com
        worker_instance_type: m5.4xlarge
        worker_replicas: 3
        master_instance_type: c5.4xlarge
        master_replicas: 3
        ssh_pubkey: '{specify or leave blank}'
```

