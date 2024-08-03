#!/usr/bin/python

# Copyright: (c) 2024, Ram Gopinathan <rprakashg@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
module: tester

short_description: tester moduler for running cli commands

description: tester module for running cli commands in subprocess and capture output

options:
    command:
        description: Command to run
        type: str
        required: true
    args:
        description: Command arguments
        type: str
        required: true

notes: []
'''

EXAMPLES = r'''
- name: test 1

'''
from ansible.module_utils.basic import AnsibleModule  # noqa E402
from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.helper import Helper

import subprocess

def run_module(module, helper):
    command = module.params["command"]
    args = module.params["args"]
    
    result = helper.run_command("openshift-install", "version")
    module.exit_json(**result)

def main():
    module_args = dict(
        command=dict(type=str, required=True),
        args=dict(type=str, required=True)
    )
    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    helper = Helper()
    run_module(module, helper)

if __name__ == '__main__':
    main()