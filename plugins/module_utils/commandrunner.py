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
        command = [self.binary, command, subcommand] + args        
        #run_command = self.binary + command + subcommand + "".join(args)

        try:
            resp = subprocess.run(command, shell=True, check=True, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    text=True)
            return CommandResult(
                exit_code=resp.returncode,
                output=resp.stdout.strip() if resp.stdout else "stdout is empty",
                error=resp.stderr.strip() if resp.stderr else "stderr is empty"
            )
        except subprocess.CalledProcessError as e:
            # Handle errors from running the command
            return CommandResult(
                exit_code=e.returncode,
                output=e.stdout.strip() if e.stdout else "stdout is empty",
                error=e.stderr.strip() if e.stderr else "stderr is empty"
            )
        return resp