#!/usr/bin/env python3

# DEPENDENCIES
## Built-In
import json
import os
import subprocess
from subprocess import Popen
import sys
import tarfile
from time import sleep
from typing import IO
## Third-Party
from tqdm import tqdm


# CONSTANTS
CONTAINER_NAME: str = "l4t-20.04"
class Paths:
    CONFIG: str = "config"
    TEMP_CONTAINERFILES: str = "temp"
    ASSETS: str = "assets"
class ConfigKeys:
    PYTHON_VERSION: str = "python_version"
    OPENCV_VERSION: str = "opencv_version"
    PYTORCH_VERSION: str = "pytorch_version"
    TORCHVISION_VERSION: str = "torchvision_version"
    TENSORRT_VERSION: str = "tensorrt_version"
class Containerfiles:
    BASE: str = "Containerfile.base"
    COMPILE_OPENCV: str = "Containerfile.compile_opencv"
    COMPILE_PYTORCH: str = "Containerfile.compile_pytorch"
    COMPILE_TENSORRT: str = "Containerfile.compile_tensorrt"
class Tags:
    BASE: str = "base"
    OPENCV: str = "opencv"
    PYTORCH: str = "pytorch"
    TENSORRT: str = "tensorrt"
    FINAL: str = "latest"
class VariableReferences:
    CONTAINER_NAME: str = "{{ image_name }}"
    BASE_CONTAINER_TAG: str = "{{ base_tag }}"
    PYTHON_VERSION: str = "{{ python_version }}"
    OPENCV_VERSION: str = "{{ opencv_version }}"
    PYTOCH_VERSION: str = "{{ pytorch_version }}"
    TORCHVISION_VERSION: str = "{{ torchvision_version }}"
    TENSORRT_VERSION: str = "{{ tensorrt_version }}"


# HELPERS
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

def get_config() -> dict[str, str]:
    with open(Paths.CONFIG, "r") as config_file:
        config = json.load(config_file)
        return config
CYTHON_VERSION: str = f"cu{get_config()[ConfigKeys.PYTHON_VERSION].replace('.', '')}"


# SETUP
def _setup() -> None:
    if not os.path.exists(Paths.TEMP_CONTAINERFILES):
        os.makedirs(Paths.TEMP_CONTAINERFILES)
    if not os.path.exists(Paths.ASSETS):
        os.makedirs(Paths.ASSETS)

# BUILDING
def _build_base_image() -> None:
    print("Creating Base Containerfile...")
    base_containerfile_original: str = ""
    with open(f"{Containerfiles.BASE}", "r") as base_file:
        base_containerfile_original = base_file.read()
    with open(f"{Paths.TEMP_CONTAINERFILES}/{Containerfiles.BASE}", "w") as base_file:
        base_containerfile = base_containerfile_original.replace(VariableReferences.PYTHON_VERSION, get_config()[ConfigKeys.PYTHON_VERSION])
        base_file.write(base_containerfile)
    custom_tag: str = f"{Tags.BASE}={CYTHON_VERSION}"
    build_command: str = f"docker build -t {CONTAINER_NAME}:{custom_tag} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.BASE} ."
    execute(build_command)

## Compiling Steps
def _build_opencv_deb() -> None:
    print("\nCreating OpenCV Containerfile...")
    compile_opencv_containerfile_original: str = ""
    with open(f"{Containerfiles.COMPILE_OPENCV}", "r") as compile_opencv_file:
        compile_opencv_containerfile_original = compile_opencv_file.read()
    with open(f"{Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_OPENCV}", "w") as compile_opencv_file:
        compile_opencv_containerfile: str = compile_opencv_containerfile_original.replace(VariableReferences.CONTAINER_NAME, CONTAINER_NAME)
        compile_opencv_containerfile = compile_opencv_containerfile.replace(VariableReferences.BASE_CONTAINER_TAG, Tags.BASE)
        compile_opencv_containerfile = compile_opencv_containerfile.replace(VariableReferences.OPENCV_VERSION, get_config()[ConfigKeys.OPENCV_VERSION])
        compile_opencv_file.write(compile_opencv_containerfile)
    
    print("\nCompiling OpenCV debs...")
    custom_tag: str = f"{Tags.OPENCV}-{CYTHON_VERSION}"
    build_command: str = f"docker build -t {CONTAINER_NAME}:{custom_tag} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_OPENCV} ."
    execute(build_command)
    
    print("\nExtracting OpenCV Debs...")
    sleep(1)
    extract_assets_command: str = f"docker run --rm -it -v {os.getcwd()}/{Paths.ASSETS}:/home/assets {CONTAINER_NAME}:{Tags.OPENCV}"
    execute(extract_assets_command)

    print("Cleaning up Image...")
    remove_image_command: str = f"docker rmi {CONTAINER_NAME}:{custom_tag}"
    execute(remove_image_command)
    
    print("\nCompressing OpenCV Debs...")
    opencv_version: str = get_config()[ConfigKeys.OPENCV_VERSION]
    tar_file_name: str = f"opencv{opencv_version}-{CYTHON_VERSION}.tar.gz"

    with tarfile.open(os.path.join(Paths.ASSETS, tar_file_name), 'w:gz') as tar_file:
        for root, dirs, files in os.walk(Paths.ASSETS):
            for file in tqdm(files, desc="Compressing files", unit="files"):
                file_path: str = os.path.join(root, file)
                tar_file.add(file_path, arcname=file_path)

    print("\nRemoving OpenCV Debs...")
    for root, dirs, files in os.walk(Paths.ASSETS):
        for file in tqdm(files, desc="Removing files", unit="files"):
            file_path = os.path.join(root, file)
            if file != tar_file_name:
                os.remove(file_path)
        for dir in tqdm(dirs, desc="Removing dirs", unit="dirs"):
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)

def _build_pytorch_deb() -> None:
    pass

def _build_tensorrt_wheel() -> None:
    pass

## Final Image
def _build_final_image() -> None:
    pass


# MAIN
def main() -> None:
    _setup()
    #_build_base_image()
    #_build_opencv_deb()
    _build_pytorch_deb()
    _build_tensorrt_wheel()
    _build_final_image()
    print("\nFull Build Process Completed!\n")


if __name__ == "__main__":
    main()
