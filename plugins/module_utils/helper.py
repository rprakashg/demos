import re
import subprocess
import os

class Helper(object):
    """
        Helper

        This is a helper utility class
    """  
    def __init__(self) -> None:
        return
    
    def parse_installer_output(self, output):
        """
        Parse tokens from the output of openshift installer cli create cluster command 
        :output: Stdout string

        :return: Any
        """

        if output is None:
            return None
        
        result = dict(
            api_server_url=dict(type=str, required=True),
            web_console_url=dict(type=str, required=True),
            set_kubeconfig_cmd=dict(type=str, required=True),
            user=dict(type=str, required=True),
            password=dict(type=str, required=True)
        )

        # Regex patterns to extract
        api_url_pattern = re.compile(r'Kubernetes API at (https://\S+)', re.IGNORECASE)
        console_url_pattern = re.compile(r'OpenShift web-console here: (https://\S+)', re.IGNORECASE)
        set_kubeconfig_cmd_pattern = re.compile(r'run \'(export KUBECONFIG=\S+)\'', re.IGNORECASE)
        credentials_pattern=re.compile(r'user: "(.*)", and passwprd: "(.*)"', re.IGNORECASE)

        api_url = re.search(api_url_pattern, output)
        console_url = re.search(console_url_pattern, output)
        set_kubeconfig_cmd = re.search(set_kubeconfig_cmd_pattern, output)
        credentials = re.search(credentials_pattern, output)

        result['api_server_url'] = api_url.group(1) if api_url else None
        result['web_console_url'] = console_url.group(1) if console_url else None
        result['set_kubeconfig_cmd'] = set_kubeconfig_cmd.group(1) if set_kubeconfig_cmd else None
        result['user'] = credentials.group(1) if credentials else None
        result['password'] = credentials.group(2) if credentials else None
        
        return result
    
    #def get_collection_path(self, namespace, name):
    #    collection_paths = loader.collections_paths()

    #    for path in collection_paths:
    #        p = os,path.join(path, 'ansible_collections', namespace, name)
    #        if os.path.isdir(p):
    #            return p
    #    return None
         
    def run_command(self, binary, args):
        result = dict(
            exit_code=0,
            output="",
            error=""
        )
        run_command = binary + " " + " ".join(args)
        raise Exception(run_command)
    
        process = subprocess.Popen(run_command, shell=True, text=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline()
            if line:
                result["output"] += line
            err = process.stderr.readline()
            if err:
                result["error"] += err
            if line == '' and err == '' and process.poll() is not None:
                break
                
        result["exit_code"] = process.poll()

        return result