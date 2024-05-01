# DEPENDENCIES
## Built-In
import json
import subprocess
from subprocess import Popen
import sys
from typing import IO


# CONSTANTS
CONFIG_PATH: str = "config"


# CONFIG
def get_config() -> dict[str, str]:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
        return config


# SHELL
def execute(
    command: str,
    should_print_result: bool = True,
    ignore_error: bool = False,
    error_message: str = ""
) -> str:
    if not error_message:
        error_message = f"Unable to execute command: {command}"
    command_list: tuple[str, ...] = tuple(command.split())
    process: Popen = subprocess.Popen(command_list, stdout=subprocess.PIPE, text=True)
    if should_print_result:
        has_printed: bool = False
        while process.poll() is None:
            if not process.stdout:
                continue
            print_lines: IO = process.stdout
            if has_printed:
                for _ in print_lines:
                    sys.stdout.write("\033[F")  # Move cursor up one line
                    sys.stdout.write("\033[K") # Clear line
            for line in print_lines:
                print(line, end="")
            has_printed = True
    if process.returncode != 0 and not ignore_error:
        raise Exception(error_message)
    stdout, stderr = process.communicate()
    return stdout
