#!/usr/bin/python

# Copyright: (c) 2024, Ram Gopinathan <rprakashg@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: download_pullsecret

short_description: Download Red Hat pullsecret

description: 
 - Download Red Hat pullsecret from console.redhat.com/openshift/downloads using API

author:
 - Ram Gopinathan (@rprakashg) 

options:

notes: []

'''

EXAMPLES = r'''
- name: Download pullsecret
  rprakashg.demos.download_pullsecret:
    offline_token: "{{ offline_token }}"  
'''

from ansible.module_utils.basic import AnsibleModule  # noqa E402
import requests

TOKEN_ENDPOINT = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
GRANT_TYPE = "refresh_token"
CLIENT_ID = "rhsm-api"
PULLSECRET_API = "https://api.openshift.com/api/accounts_mgmt/v1/access_token"

def run_module(module):
    params: dict = module.params
    result = dict(
        pull_secret="",
    )
    # first get access token from offline token
    payload = {
        "grant_type": GRANT_TYPE,
        "refresh_token": params["offline_token"],
        "client_id": CLIENT_ID
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(TOKEN_ENDPOINT, data=payload, headers=headers)
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to retrieve access token: {response.text}")

    access_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(PULLSECRET_API, headers=headers)
    if response.status_code != 200:
        module.fail_json(msg=f"Failed to download Red Hat pull secret: {response.text}")
    
    result["pull_secret"] = response.json()
    module.exit_json(msg="Successfully retrieved Red Hat pullsecret", **result)

def main():
    module_args = dict(
        offline_token = dict(type=str, required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    run_module(module)

if __name__ == '__main__':
    main()