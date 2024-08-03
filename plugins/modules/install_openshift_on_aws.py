#!/usr/bin/python

# Copyright: (c) 2024, Ram Gopinathan <rprakashg@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: install openshift on aws

short_description: Install Openshift cluster on AWS

description: 
    - Install Openshift container platform cluster on AWS

author:
    - Ram Gopinathan (@rprakashg)

options:
    cluster_name:
        description: Cluster name
        type: str
        required: true
    region:
        description: AWS Region to provision the cluster
        type: str
        required: true
    base_domain:
        description: Base domain for cluster
        type: str
        required: true
    worker_instance_type:
        description: Instancy type to be used for compute/worker nodes
        type: str
        required: true
        default: m5.4xlarge
    worker_replicas:
        description: Number of worker/compute nodes
        type: int
        required: true
        default: 1
    master_instance_type:
        description: Instance type to be used for master/controlplane nodes
        type: str
        required: true
        default: c5.4xlarge
    master_replicas:
        description: Number of replicas for master/controlplane nodes
        type: int
        default: 3
        required: true
    ssh_pubkey:
        description: SSH public key, if no key is passed will try to default parse the id_rs.pub key from ~/.ssh directory
        type: str
        required: false
    pull_secret:
        description: Red Hat pull secret
        type: str
        required: false
    offline_token:
        description: Offline token, this is only required if a pull secret is not specified. This token is used to automatically download pull secret from cloud.redhat.com. If an offline token and pull secret is not specified as inputs the module will try to read token from environment variable 'RH_OFFLINE_TOKEN'
        type: str
        required: false
notes: []

'''

EXAMPLES = r'''
- name: install openshift on aws
  rprakashg.automation.install_openshift_on_aws:
    cluster_name: hub
    region: us-west-2
    base_domain: ocp.example.com
    worker_instance_type: m5.4xlarge
    worker_replicas: 3
    master_instance_type: c5.4xlarge
    master_replicas: 3
    ssh_pubkey: 'ssh-rsa AAA ... user@email.com'
    pull_secret: ''
    offline_token: ''
'''

import boto3
import os
import requests
import json
import yaml
import tempfile

from ansible.module_utils.basic import AnsibleModule  # noqa E402
from jinja2 import Environment, FileSystemLoader
from itertools import islice

from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.helper import Helper

def get_azs(region, replicas):
    take: int
    if replicas > 3:
        take = 3
    else:
        take = replicas
    client = boto3.client('ec2', region_name=region)
    response = client.describe_availability_zones()
    azs = [az['ZoneName'] for az in response['AvailabilityZones']]
    
    return azs[:take]

def generate_installconfig_template():
    template = yaml.safe_load("""
    apiVersion: v1
    baseDomain: {{ base_domain }}
    compute:
    - architecture: amd64
      hyperthreading: Enabled
      name: worker
      platform:
        aws:
            zones:
            {% for az in worker_azs -%}
            - {{ az }}
            {% endfor -%}
            rootVolume:
                iops: 2000
                size: 500
                type: io1 
        type: {{ worker_instance_type }}
      replicas: {{ worker_replicas }}
    controlPlane:
        architecture: amd64
        hyperthreading: Enabled
        name: master
        platform:
            aws:
                zones:
                {% for az in controlplane_azs -%}
                - {{ az }}
                {% endfor -%}
                rootVolume:
                    iops: 4000
                    size: 500
                    type: io1 
                type: {{ master_instance_type }} 
        replicas: {{ master_replicas }}
    metadata:
        name: {{ cluster_name }}
    networking:
        clusterNetwork:
        - cidr: 10.128.0.0/14
          hostPrefix: 23
        machineNetwork:
        - cidr: 10.0.0.0/16
        networkType: OVNKubernetes
        serviceNetwork:
        - 172.30.0.0/16
    platform:
        aws:
            region: {{ region }}
    publish: External
    pullSecret: '{{ pullsecret }}'
    sshKey: |
        {{ ssh_pub_key }}
    """)   

    #Write the template to tmp directory
    try:
        template_file = tempfile.NamedTemporaryFile(delete=False,
                                    mode='w', suffix='.yaml.j2')
        yaml.dump(template, template_file)
        return template_file.name
    except Exception as e:
        return None

def generate_installconfig(params, install_config_file):
    template_file = generate_installconfig_template()
    if template_file is None: 
        return False

    template_env = Environment(loader=FileSystemLoader(tempfile.gettempdir()))
    template = template_env.get_template(template_file)

    # define context data to render install config yml
    context = {
        'cluster_name': params["cluster_name"],
        'region': params["region"],
        'controlplane_azs': params["controlplane_azs"],
        'worker_azs': params["worker_azs"], 
        'base_domain': params["base_domain"],
        'worker_instance_type': params["worker_instance_type"],
        'worker_replicas': params["worker_replicas"],
        'master_instance_type': params["master_instance_type"],
        'master_replicas': params["master_replicas"],
        'pullsecret': params["pull_secret"],
        'ssh_pub_key': params["ssh_pubkey"],
    }

    # Render template with provided variables
    rendered_content = template.render(context)

    # Write rendered content to the destination file
    with open(install_config_file, 'w') as f:
        f.write(rendered_content)

    return True

def download_pullsecret(token):
    if token is None:
        token = os.getenv("RH_OFFLINE_TOKEN")
    token_endpoint: str = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
    api: str = "https://api.openshift.com/api/accounts_mgmt/v1/access_token" 

    data = {
        'grant_type': 'refresh_token',
        'client_id': 'rhsm-api',
        'refresh_token': f'{token}'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_endpoint, data=data, headers=headers)
    response.raise_for_status()
    access_token = response.json()['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    secret_response = requests.post(api, headers=headers)
    secret_response.raise_for_status()
    return secret_response.json()

def parse_ssh_key(key_file):
    home_dir = os.path.expanduser("~")
    ssh_dir = "%s/.ssh" % (home_dir)
    pubkey = "%s/%s" % (ssh_dir, key_file)

    try:
        with open(pubkey, "r") as file:
            return file.read().strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read ssh key file: {str(e)}")

def run_module(module, helper):
    params: dict = module.params
    
    result = dict(
        api_server_url="",
        web_console_url="",
        user = "",
        password = "",
        kubeconfig = "",
        output = ""
    )

    # Check if AWS credentials are set in environment variables
    if os.getenv("AWS_ACCESS_KEY_ID") is None:
        module.fail_json(msg="AWS_ACCESS_KEY_ID could not be found in environment variables")

    if os.getenv("AWS_SECRET_ACCESS_KEY") is None:
        module.fail_json(msg="AWS_SECRET_ACCESS_KEY could not be found in environment variables")

    if os.getenv("RH_OFFLINE_TOKEN") is None and params["pull_secret"] is None:
        module.fail_json(msg="A Red Hat pull secret was not specified and also RH_OFFLINE_TOKEN was not found in environment variable to automatically download pull secret")

    # Check if aws region is specified in params if not use AWS_DEFAULT_REGION environment variable value
    if params["region"] is None and not os.getenv("AWS_DEFAULT_REGION") is None:
        params["region"] = os.getenv("AWS_DEFAULT_REGION")
    elif params["region"] is None and os.getenv("AWS_DEFAULT_REGION") is None:
        module.fail_json(msg="AWS region needs to be specified as input or using 'AWS_DEFAULT_REGION' environment variable")
            
    # Create clusters directory if one doesn't exist
    cluster_name: str = params["cluster_name"]

    home_dir = os.path.expanduser("~")
    clusters_dir = "%s/clusters/%s" % (home_dir, cluster_name)
    
    if not os.path.isdir(clusters_dir):
        os.makedirs(clusters_dir)

    try:
        # Get Azs for region
        region: str = params["region"]

        worker_azs=get_azs(region, module.params["worker_replicas"])
        master_azs=get_azs(region, module.params["master_replicas"])

        # add worker_azs and master_azs to params dict
        params.update({"worker_azs": worker_azs, "controlplane_azs": master_azs})
    except Exception as e:
        module.fail_json(msg=f"Error retrieving availability zones for region: {region}. {e}")

    if params["pull_secret"] is None:
        # Download pullsecret
        pull_secret = download_pullsecret(params["offline_token"])
        pull_secret_str = json.dumps(pull_secret)
        params["pull_secret"] = pull_secret_str

    if params["ssh_pubkey"] is None:
        # Get SSH Key
        ssh_pubkey = parse_ssh_key("id_rsa.pub")
        params["ssh_pubkey"] = ssh_pubkey
        
    # Generate install config file
    install_config = "%s/install-config.yaml" % (clusters_dir)
    generate_installconfig(params, install_config)

    # Run openshift install
    args = [
        "create",
        "cluster",
        f"--dir={clusters_dir}",
        "--log-level=info"
    ]
    cr = helper.run_command("openshift-install", args)
    if cr["exit_code"] == 0:
        result["output"] = cr["output"]
    else:
        module.fail_json(msg=cr["error"])

    #parse tokens from installer output
    tokens = helper.parse_installer_output(result["output"])
    if tokens is not None:
        result["api_server_url"] = tokens["api_server_url"]
        result["web_console_url"] = tokens["web_console_url"]
        result["kubeconfig"] = tokens["set_kubeconfig_cmd"]
        result["user"] = tokens["user"]
        result["password"] = tokens["password"]

    # Exit the module and return results
    title = "Openshift cluster %s was created successfully" % (params["cluster_name"])
    module.exit_json(msg=title, **result, changed=True)

def main():
    module_args = dict(
        cluster_name=dict(type=str, required=True),
        region=dict(type=str, required=False),
        base_domain=dict(type=str, required=True),
        worker_instance_type=dict(type=str, required=True),
        worker_replicas=dict(type=int, required=True),
        master_instance_type=dict(type=str, required=True),
        master_replicas=dict(type=int, required=True),
        ssh_pubkey=dict(type=str, required=False),
        pull_secret=dict(type=str, required=False),
        offline_token=dict(type=str, required=False)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    helper = Helper()

    run_module(module, helper)
    
if __name__ == '__main__':
    main()