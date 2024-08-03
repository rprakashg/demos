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

import subprocess

def run_module(module):
    command = module.params["command"]
    args = module.params["args"]
    result = dict(
        exit_code=0,
        output="",
        error=""
    )

    process = subprocess.Popen(command + " " + args, shell=True, text=True,
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if line:
            result["output"] += line.strip()
        err = process.stderr.readline()
        if err:
            result["error"] += err
        if line == '' and process.poll() is not None:
            break

    result["exit_code"] = process.poll()

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
    run_module(module)

if __name__ == '__main__':
    main()