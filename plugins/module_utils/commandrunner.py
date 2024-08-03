import subprocess
from ansible_collections.rprakashg.openshift_automation.plugins.module_utils.commandresult import CommandResult

class CommandRunner(object):
    """
        CommandRunner

        This is a helper utility for running commandline binaries
    """    
    def __init__(self, binary, module) -> None:
        self.binary = binary
        self.module = module

    def run(self, command, subcommand, args) -> CommandResult:
        """
        Run command with subcommand and args in an executable binary

        :command: Command to execute
        :subcommand: Sub command to execute
        :args: Array of command line arguments for the sub command being executed

        :return: CommandResult
        """
        run_command = " ".join([self.binary, command, subcommand] + args)
        self.module.stdout.write(f"Running command : {run_command}")
        result = CommandResult(exit_code=0, output="", error="")
        try:
            process = subprocess.Popen(run_command, shell=True, text=True,
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
            while True:
                line = process.stdout.readline()
                if line == '' and process.poll() is not None:
                    break
                if line:
                    result.output += line.strip()
                    self.module.stdout.write(line)
                    self.module.stdout.flush()
            
            err = process.stderr.read()
            if err:
                self.module.stderr.write(err)
                self.module.stderr.flush()
                result.error = err
                
        except subprocess.CalledProcessError as e:
            # Handle errors from running the command
            result.exit_code=e.returncode
            result.output=e.stdout.strip() if e.stdout else "stdout is empty",
            result.error=e.stderr.strip() if e.stderr else "stderr is empty"
        
        return result
