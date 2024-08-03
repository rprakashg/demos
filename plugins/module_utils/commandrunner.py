import subprocess
from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.commandresult import CommandResult

class CommandRunner(object):
    """
        CommandRunner

        This is a helper utility for running commandline binaries
    """    
    def __init__(self, binary) -> None:
        self.binary = binary

    def run(self, command, subcommand, args) -> CommandResult:
        """
        Run command with subcommand and args in an executable binary

        :command: Command to execute
        :subcommand: Sub command to execute
        :args: Array of command line arguments for the sub command being executed

        :return: CommandResult
        """
        run_command = " ".join([self.binary, command, subcommand] + args)
        result = CommandResult(exit_code=0, output="", error="")

        process = subprocess.Popen(run_command, shell=True, text=True,
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline()
            if line:
                result.output += line.strip()            
            err = process.stderr.readline()
            if err:
                result.error += err
            if line == '' and err == '' and process.poll() is not None:
                break    

        result.exit_code = process.poll()
        
        return result
