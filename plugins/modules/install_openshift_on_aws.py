#!/usr/bin/python

# Copyright: (c) 2024, Ram Gopinathan <rprakashg@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "0.1",
    "status": ["preview"],
    "supported_by": "Community"
}

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
'''

import boto3
import yaml 
import os
import re
import base64 
import requests
import json

from ansible.module_utils.basic import AnsibleModule  # noqa E402
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from jinja2 import Environment, FileSystemLoader
from itertools import islice

from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.commandrunner import CommandRunner
from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.commandresult import CommandResult

def read_vault_file(vault_file, vault_password):
    vault_secret = VaultSecret(base64.b64encode(vault_password.encode('utf-8')))
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, vault_secret)])

    # Read the vault file content
    with open(vault_file, 'rb') as f:
        vault_content = f.read()

    # Decrypt the vault content
    decrypted_content = vault.decrypt(vault_content).decode('utf-8')

    return decrypted_content

def get_azs(region, replicas):
    take: int
    if replicas > 3:
        take = 3
    else:
        take = replicas
    client = boto3.client('ec2', region_name=region)
    response = client.describe_availability_zones()
    azs = [az['ZoneName'] for az in response['AvailabilityZones']]
    return dict(islice(azs, take))
    
def generate_installconfig(params, secrets, install_config_file):

    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('install-config-aws.yml.j2')

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
        'pullsecret': secrets["pull_secret"],
        'ssh_pub_key': params["ssh_pubkey"],
    }

    # Render template with provided variables
    rendered_content = template.render(context)

    # Write rendered content to the destination file
    with open(install_config_file, 'w') as f:
        f.write(rendered_content)

    return True

def download_pullsecret(rh_offline_token):
    token_endpoint: str = "https://sso.redhat.com/auth/realms/redirect-external/protocol/openid-connect/token"
    api: str = "https://api.openshift.com/api/accounts_mgmt/v1/access_token" 

    data = {
        'grant_type': 'refresh_token',
        'client_id': 'rhsm-api',
        'refresh_token': f'{rh_offline_token}'
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

def parse_token(pattern: str, log_content: str):
    match = re.search(pattern, log_content, re.IGNORECASE)
    if match:
        return match
    else:
        raise ValueError(f"Pattern not found {pattern}")

def install_openshift(module, runner):
    params: dict = module.params
    
    result = dict(
        api_server_url = dict(type=str),
        web_console_url = dict(type=str),
        credentials = dict(
            user = dict(type=str),
            password = dict(type=str)
        ),
        kubeconfig = dict(type=str),
        output = dict(type=str)
    )

    error_payload = dict(
        changed = dict(type=bool, required=True),
        error_msg = dict(type=str, required=True)
    )

    # Check if AWS credentials are set in environment variables
    if os.getenv("AWS_ACCESS_KEY_ID") is None:
        error_payload["error_msg"] = "AWS_ACCESS_KEY_ID could not be found in environment variables"
        error_payload["changed"] = False
        module.fail_json(error_payload)

    if os.getenv("AWS_SECRET_ACCESS_KEY") is None:
        error_payload["error_msg"] = "AWS_SECRET_ACCESS_KEY could not be found in environment variables"
        error_payload["changed"] = False 
        module.fail_json(error_payload)

    if os.getenv("VAULT_SECRET") is None:
        error_payload["error_msg"] = "VAULT_SECRET could not be found in environment variables"
        error_payload["changed"] = False
        module.fail_json(error_payload)

    # check if vault secrets file exists
    if os.path.exists("vars/secrets.yml") is None:
        error_payload["error_msg"] = "Ansible vault file is required"
        error_payload["changed"] = False
        module.fail_json(error_payload)

    # Check if aws region is specified in params if not use AWS_DEFAULT_REGION environment variable value
    if params["region"] is None and not os.getenv("AWS_DEFAULT_REGION") is None:
        params["region"] = os.getenv("AWS_DEFAULT_REGION")
    elif params["region"] is None and os.getenv("AWS_DEFAULT_REGION") is None:
        error_payload["error_msg"] = "AWS region needs to be specified as input or using 'AWS_DEFAULT_REGION' environment variable"
        error_payload["changed"] = False
        module.fail_json(error_payload)
            
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
    except:
        error_payload["error_msg"] = f"Error retrieving availability zones for region: {region}"
        error_payload["changed"] = False
        module.fail_json(error_payload)

    # decrypt the ansible vault
    vault_secret = os.getenv("VAULT_SECRET")
    content = read_vault_file("vars/secrets.yml", vault_secret)
    secrets = yaml.safe_load(content)

    if secrets["pull_secret"] is None:
        # Download pullsecret
        pull_secret = download_pullsecret(secrets["rh_offline_token"])
        pull_secret_str = json.dumps(pull_secret)
        secrets["pull_secret"] = pull_secret_str

    if module.params["ssh_pubkey"] is None:
        # Get SSH Key
        ssh_pubkey = parse_ssh_key("~/.ssh/id_rsa.pub")
        module.params["ssh_pubkey"] = ssh_pubkey
        
    # Generate install config file
    install_config = "%s/install-config.yml" % (clusters_dir)
    generate_installconfig(module.params, secrets, install_config)

    # Run openshift install
    args = [
        "--dir=",
        clusters_dir,
        "--log-level=",
        "info"
    ]
    result: CommandResult = runner.run("create", "cluster", args)
    if result.exit_code == 0:
        output = result.output
    else:
        module.fail_json()

    # Parse kube api server url from output and set it to result
    api_pattern = r'Kubernetes API at ([^\s]+)'
    api_server_url = parse_token(api_pattern, output)
    result["api_server_url"] = api_server_url

    # Parse openshift webconsole URL from output and set it in result
    webconsole_pattern = r'weh-console here: ([^\s]+)'
    webconsole_url = parse_token(webconsole_pattern, output)
    result["web_console_url"] = webconsole_url

    # Parse cluster credentials from output and set it in result
    user_pattern = r'user:\s*"([^"]+)"' 
    password_pattern = r'passwprd:\s*"([^"]+)"'    
    user = parse_token(user_pattern, output)
    password = parse_token(password_pattern, output)
    result["credentials"].update({
        "user": user,
        "password": password,
    })

    # Parset kubeconfig path from output and set it in result
    kubeconfig_pattern = r'export KUBECONFIG=([^\s]+)'
    kubeconfig_path = parse_token(kubeconfig_pattern, output)
    result["kubeconfig"] = kubeconfig_path
    
    result["output"] = output

    # Exit the module and return results
    module.exit_json(msg="Openshift cluster %s was created successfully" % (params["cluster_name"]), 
                     result=result, changed=True)

def main():
    module_args = dict(
        cluster_name=dict(type=str, required=True),
        region=dict(type=str, required=False),
        base_domain=dict(type=str, required=True),
        worker_instance_type=dict(type=str, required=True),
        worker_replicas=dict(type=int, required=True),
        master_instance_type=dict(type=str, required=True),
        master_replicas=dict(type=int, required=True),
        ssh_pubkey=dict(type=str, required=False)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    binary = "openshift-install"
    runner: CommandRunner = CommandRunner(binary)

    install_openshift(module, runner)
    
if __name__ == '__main__':
    main()