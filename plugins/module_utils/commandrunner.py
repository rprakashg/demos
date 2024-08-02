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

        try:
            process = subprocess.Popen(run_command, shell=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                result["ouput"] += line.strip()
                
            process.stdout.close()
            process.wait()
            result.exit_code = process.returncode
            if process.returncode != 0:
                result.error = process.stderr.read() if process.stderr else None

        except subprocess.CalledProcessError as e:
            # Handle errors from running the command
            result.exit_code=e.returncode,
            result.error=e.stderr.strip() if e.stderr else "stderr is empty"

        return result