import subprocess
from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.commandresult import CommandResult

class CommandRunner(object):
    """
        CommandRunner

        This is a helper utility for running commandline binaries
    """    
    def __init__(self, binary, logger) -> None:
        self.binary = binary
        self.logger = logger

    def run(self, command, subcommand, args) -> CommandResult:
        """
        Run command with subcommand and args in an executable binary

        :command: Command to execute
        :subcommand: Sub command to execute
        :args: Array of command line arguments for the sub command being executed

        :return: CommandResult
        """
        run_command = self.binary + command + subcommand + "".join(args)
        self.logger.info("Run command: %s" %(run_command))

        p = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                text=True)
        
        result = CommandResult(exit_code=0, output="", error="")

        while True:
            line = p.stdout.readline().strip()
            if line == '' and p.poll() is not None:
                break
            if line:
                self.logger.info(msg=line)
                result.output += line
            error = p.stderr
            if error:
                self.module.warn(msg=error.strip())
                result.error = error.strip()

        result.exit_code = p.returncode

        return result


