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

        try:
            result = subprocess.run(run_command, shell=True, check=True, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    text=True)
            return CommandResult(
                exit_code=result.returncode,
                output=result.stdout.strip(),
                error=result.stderr.strip()
            )
        except subprocess.CalledProcessError as e:
            # Handle errors from running the command
            return CommandResult(
                exit_code=e.returncode,
                output=e.stdout.strip() if e.stdout else "",
                error=e.stderr.strip() if e.stderr else ""
            )
        
        #p = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE, 
        #                     stderr=subprocess.PIPE, text=True)
        #result = CommandResult(exit_code=0, output="", error="")

        #while True:
        #    line = p.stdout.readline().strip()
        #    if line == '' and p.poll() is not None:
        #        break
        #    if line:
        #        self.logger.info(line)
        #        result.output += line
        #    error = p.stderr
        #    if error:
        #        self.logger.warn(error.strip())
        #        result.error = error.strip()

        # result.exit_code = p.returncode

        #return result