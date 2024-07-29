from dataclasses import dataclass

@dataclass
class CommandResult:
    exit_code: int
    output: str
    error: str
