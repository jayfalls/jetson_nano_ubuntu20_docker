# DEPENDENCIES
## Built-In
import json
import os
import shlex
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
def execute(command: str, should_print_result: bool = True, ignore_error: bool = False, error_message: str = "") -> str:
    if not error_message:
        error_message = f"Unable to execute command: {command}"
    print(f"Running Command: {command}")
    command_list: tuple[str, ...] = tuple(shlex.split(command))
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
    stdout, stderr = process.communicate()
    if process.returncode != 0 and not ignore_error:
        print(stderr)
        print(error_message)
        os._exit(1)
    return stdout

def exec_check_exists(check_command: str, keyword: str) -> bool:
    """
    Checks if a given keyword exists in the output of a given shell command

    Arguments:
        check_command (str): The shell command to be executed
        keyword (str): The keyword to be searched for
    
    Returns:
        bool: True if the keyword is found, False otherwise
    """
    print(f"\nChecking using command: '{check_command}', for keyword '{keyword}'...")
    exec_output: str | Popen = execute(check_command, should_print_result=False, ignore_error=True)
    if isinstance(exec_output, Popen):
        raise Exception("Something went wrong when trying to execute the command, it returned the shell process instead of a string...")
    existing = frozenset(exec_output.split("\n"))
    print(f"Existing Terms: {existing}")
    for entry in existing:
        if keyword in entry:
            return True
    return False
