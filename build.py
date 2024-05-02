#!/usr/bin/env python3

# DEPENDENCIES
## Built-In
import os
import tarfile
from time import sleep
## Third-Party
from tqdm import tqdm
## Local
from helpers import get_config, execute, exec_check_exists


# CONSTANTS
CONTAINER_NAME: str = "l4t-20.04"
class Paths:
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
    FULL: str = "Containerfile.full"
class _BaseTags:
    BASE: str = "base"
    OPENCV: str = "opencv"
    PYTORCH: str = "pytorch"
    TENSORRT: str = "tensorrt"
    FULL: str = "full"
CYTHON_VERSION: str = f"cp{get_config()[ConfigKeys.PYTHON_VERSION].replace('.', '')}"
class Tags:
    BASE: str = f"{_BaseTags.BASE}-{CYTHON_VERSION}"
    OPENCV: str = f"{_BaseTags.OPENCV}-{CYTHON_VERSION}"
    PYTORCH: str = f"{_BaseTags.PYTORCH}-{CYTHON_VERSION}"
    TENSORRT: str = f"{_BaseTags.TENSORRT}-{CYTHON_VERSION}"
    FULL: str = f"{_BaseTags.FULL}-{CYTHON_VERSION}"
class ContainerCommands:
    CHECK_IMAGE: str = "docker image ls"
class VariableReferences:
    CONTAINER_NAME: str = "{{ image_name }}"
    BASE_CONTAINER_TAG: str = "{{ base_tag }}"
    ASSETS_PATH: str = "{{ assets_path }}"
    PYTHON_VERSION: str = "{{ python_version }}"
    CYTHON_VERSION: str = "{{ cython_version }}"
    OPENCV_VERSION: str = "{{ opencv_version }}"
    PYTOCH_VERSION: str = "{{ pytorch_version }}"
    TORCHVISION_VERSION: str = "{{ torchvision_version }}"
    TENSORRT_VERSION: str = "{{ tensorrt_version }}"


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
    print("Building Base Image...")
    build_command: str = f"docker build -t {CONTAINER_NAME}:{Tags.BASE} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.BASE} ."
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
        compile_opencv_containerfile = compile_opencv_containerfile.replace(VariableReferences.PYTHON_VERSION, get_config()[ConfigKeys.PYTHON_VERSION])
        compile_opencv_containerfile = compile_opencv_containerfile.replace(VariableReferences.OPENCV_VERSION, get_config()[ConfigKeys.OPENCV_VERSION])
        compile_opencv_file.write(compile_opencv_containerfile)
    
    print("\nCompiling OpenCV debs...")
    while not exec_check_exists(ContainerCommands.CHECK_IMAGE, f"{CONTAINER_NAME}:{Tags.BASE}"):
        sleep(5)
    build_command: str = f"docker build -t {CONTAINER_NAME}:{Tags.OPENCV} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_OPENCV} ."
    execute(build_command)

    print("\nExtracting OpenCV Debs...")
    while not exec_check_exists(ContainerCommands.CHECK_IMAGE, f"{CONTAINER_NAME}:{Tags.OPENCV}"):
        sleep(5)
    extract_assets_command: str = f"docker run --rm -it -v {os.getcwd()}/{Paths.ASSETS}:/home/assets {CONTAINER_NAME}:{Tags.OPENCV}"
    execute(extract_assets_command, shell=True)

    print("Cleaning up Image...")
    remove_image_command: str = f"docker rmi {CONTAINER_NAME}:{Tags.OPENCV}"
    execute(remove_image_command)
    
    print("\nCompressing OpenCV Debs...")
    opencv_version: str = get_config()[ConfigKeys.OPENCV_VERSION]
    tar_file_name: str = f"opencv{opencv_version}-{CYTHON_VERSION}.tar.gz"

    with tarfile.open(os.path.join(Paths.ASSETS, tar_file_name), 'w:gz') as tar_file:
        for root, dirs, files in os.walk(Paths.ASSETS):
            for file in tqdm(files, desc="Compressing files", unit="files"):
                file_path: str = os.path.join(root, file)
                tar_file.add(file_path, arcname=file)

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
    print("\nCreating Full Containerfile...")
    full_containerfile_original: str = ""
    with open(f"{Containerfiles.FULL}", "r") as final_file:
        full_containerfile_original = final_file.read()
    with open(f"{Paths.TEMP_CONTAINERFILES}/{Containerfiles.FULL}", "w") as final_file:
        full_containerfile: str = full_containerfile_original.replace(VariableReferences.CONTAINER_NAME, CONTAINER_NAME)
        full_containerfile = full_containerfile.replace(VariableReferences.BASE_CONTAINER_TAG, Tags.BASE)
        full_containerfile = full_containerfile.replace(VariableReferences.ASSETS_PATH, Paths.ASSETS)
        full_containerfile = full_containerfile.replace(VariableReferences.CYTHON_VERSION, CYTHON_VERSION)
        full_containerfile = full_containerfile.replace(VariableReferences.OPENCV_VERSION, get_config()[ConfigKeys.OPENCV_VERSION])
        final_file.write(full_containerfile)
    print("Building Full Image...")
    build_command: str = f"docker build -t {CONTAINER_NAME}:{Tags.FULL} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.FULL} ."
    execute(build_command)


# MAIN
def main() -> None:
    print("Starting Compile & Build Process...")
    _setup()
    _build_base_image()
    _build_opencv_deb()
    _build_pytorch_deb()
    _build_tensorrt_wheel()
    _build_final_image()
    print("\nFull Build Process Completed!\n")


if __name__ == "__main__":
    main()
