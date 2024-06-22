#!/usr/bin/env python3

# DEPENDENCIES
## Built-In
import argparse
import os
import shutil
import tarfile
from time import sleep
## Third-Party
import docker
from docker import DockerClient
from docker.errors import ImageNotFound
from tqdm import tqdm
## Local
from helpers import get_config, execute


# CONSTANTS
CONTAINER_NAME: str = "l4t-20.04"
class Paths:
    TEMP_CONTAINERFILES: str = "temp"
    ASSETS: str = "assets"
class ArgumentNames:
    FORCE_COMPILE: str = "force-compile"
class ConfigKeys:
    PYTHON_VERSION: str = "python_version"
    OPENCV_VERSION: str = "opencv_version"
    PYTORCH_VERSION: str = "pytorch_version"
    TORCHVISION_VERSION: str = "torchvision_version"
    TORCHAUDIO_VERSION: str = "torchaudio_version"
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
class ImageNames:
    BASE: str = f"{CONTAINER_NAME}:{Tags.BASE}"
    COMPILE_OPENCV: str = f"{CONTAINER_NAME}:{Tags.OPENCV}"
    COMPILE_TORCH: str = f"{CONTAINER_NAME}:{Tags.PYTORCH}"
    COMPILE_TENSORRT: str = f"{CONTAINER_NAME}:{Tags.TENSORRT}"
class ContainerCommands:
    CHECK_IMAGE: str = "docker image ls"
class VariableReferences:
    CONTAINER_NAME: str = "{{ image_name }}"
    BASE_CONTAINER_TAG: str = "{{ base_tag }}"
    ASSETS_PATH: str = "{{ assets_path }}"
    PYTHON_VERSION: str = "{{ python_version }}"
    PYTHON_MINOR_VERSION: str = "{{ python_minor_version }}"
    CYTHON_VERSION: str = "{{ cython_version }}"
    OPENCV_VERSION: str = "{{ opencv_version }}"
    PYTORCH_VERSION: str = "{{ pytorch_version }}"
    TORCHVISION_VERSION: str = "{{ torchvision_version }}"
    TORCHAUDIO_VERSION: str = "{{ torchaudio_version }}"
    TENSORRT_VERSION: str = "{{ tensorrt_version }}"


# HELPERS
def _check_asset(tar_file_path: str) -> bool:
    print(f"Checking if {tar_file_path} exists...")
    if os.path.exists(tar_file_path):
        print(f"{tar_file_path} already exists. Skipping...")
        return True
    return False


# SETUP
def _setup() -> None:
    if not os.path.exists(Paths.TEMP_CONTAINERFILES):
        os.makedirs(Paths.TEMP_CONTAINERFILES)
    if not os.path.exists(Paths.ASSETS):
        os.makedirs(Paths.ASSETS)


# ARGUMENTS
def _parse_args() -> dict[str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument(f"--{ArgumentNames.FORCE_COMPILE}", action="store_true")
    normal_args: dict[str, bool] = vars(parser.parse_args())
    fixed_keys_args: dict[str, bool] = {}
    for key, value in normal_args.items():
        fixed_keys_args[key.replace("_", "-")] = value
    return fixed_keys_args


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
    build_base_command: str = f"docker build -t {ImageNames.BASE} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.BASE} ."
    execute(build_base_command)

## Compiling Steps
def _build_opencv_deb(force_compile: bool) -> None:
    opencv_version: str = get_config()[ConfigKeys.OPENCV_VERSION]
    tar_file_name: str = f"opencv{opencv_version}-{CYTHON_VERSION}.tar.gz"
    tar_file_path: str = os.path.join(Paths.ASSETS, tar_file_name)
    if not force_compile:
        if _check_asset(tar_file_path):
            return

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
    docker_client: DockerClient = docker.from_env()
    while True:
        try:
            docker_client.images.get(ImageNames.BASE)
            break
        except ImageNotFound:
            sleep(5)
    compile_opencv_command: str = f"docker build -t {ImageNames.COMPILE_OPENCV} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_OPENCV} ."
    execute(compile_opencv_command)

    print("\nExtracting OpenCV Debs...")
    while True:
        try:
            docker_client.images.get(ImageNames.COMPILE_OPENCV)
            break
        except ImageNotFound:
            sleep(5)
    docker_client: DockerClient = docker.from_env()
    docker_client.containers.run(
        image=ImageNames.COMPILE_OPENCV,
        volumes={f"{os.getcwd()}/{Paths.ASSETS}": {"bind": "/home/assets", "mode": "rw"}},
        remove=True,
        stdin_open=True,
        tty=True,
        detach=False,
        stdout=True,
        stderr=True
    )

    print("Cleaning up Image...")
    docker_client.images.remove(ImageNames.COMPILE_OPENCV)

    print("\nCompressing OpenCV Debs...")
    if os.path.exists(tar_file_path):
        os.remove(tar_file_path)
    with tarfile.open(tar_file_path, "w:gz") as tar_file:
        for root, dirs, files in os.walk(Paths.ASSETS):
            for file in tqdm(files, desc="Compressing files", unit="files"):
                if not file.endswith(".deb"):
                    continue
                file_path: str = os.path.join(root, file)
                tar_file.add(file_path, arcname=file)

    print("\nRemoving OpenCV Debs...")
    for root, dirs, files in os.walk(Paths.ASSETS):
        for file in tqdm(files, desc="Removing files", unit="files"):
            for dir in tqdm(dirs, desc="Removing dirs", unit="dirs"):
                dir_path: str = os.path.join(root, dir)
                os.rmdir(dir_path)
            file_path: str = os.path.join(root, file)
            if file.endswith("tar.gz"):
                continue
            os.remove(file_path)

def _build_pytorch_wheels(force_compile: bool) -> None:
    pytorch_version: str = get_config()[ConfigKeys.PYTORCH_VERSION]
    tar_file_name: str = f"pytorch{pytorch_version}-{CYTHON_VERSION}.tar.gz"
    tar_file_path: str = os.path.join(Paths.ASSETS, tar_file_name)
    if not force_compile:
        if _check_asset(tar_file_path):
            return

    print("Building PyTorch Containerfile...")
    compile_pytorch_original: str = ""
    with open(f"{Containerfiles.COMPILE_PYTORCH}", "r") as compile_pytorch_file:
        compile_pytorch_original = compile_pytorch_file.read()
    with open(f"{Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_PYTORCH}", "w") as compile_pytorch_file:
        compile_pytorch: str = compile_pytorch_original.replace(VariableReferences.CONTAINER_NAME, CONTAINER_NAME)
        compile_pytorch = compile_pytorch.replace(VariableReferences.BASE_CONTAINER_TAG, Tags.BASE)
        compile_pytorch = compile_pytorch.replace(VariableReferences.PYTORCH_VERSION, get_config()[ConfigKeys.PYTORCH_VERSION])
        compile_pytorch = compile_pytorch.replace(VariableReferences.TORCHVISION_VERSION, get_config()[ConfigKeys.TORCHVISION_VERSION])
        compile_pytorch = compile_pytorch.replace(VariableReferences.TORCHAUDIO_VERSION, get_config()[ConfigKeys.TORCHAUDIO_VERSION])
        compile_pytorch_file.write(compile_pytorch)
    
    print("Compiling PyTorch Wheels...")
    docker_client: DockerClient = docker.from_env()
    while True:
        try:
            docker_client.images.get(ImageNames.BASE)
            break
        except ImageNotFound:
            sleep(5)
    compile_pytorch_command: str = f"docker build -t {ImageNames.COMPILE_TORCH} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_PYTORCH} ."
    execute(compile_pytorch_command)

    print("Extracting PyTorch Wheels...")
    while True:
        try:
            docker_client.images.get(ImageNames.COMPILE_TORCH)
            break
        except ImageNotFound:
            sleep(5)
    docker_client.containers.run(
        image=ImageNames.COMPILE_TORCH,
        volumes={f"{os.getcwd()}/{Paths.ASSETS}": {"bind": "/home/assets", "mode": "rw"}},
        remove=True,
        stdin_open=True,
        tty=True,
        detach=False,
        stdout=True,
        stderr=True
    )

    print("Cleaning up Image...")
    docker_client.images.remove(ImageNames.COMPILE_TORCH)

    print("Compressing PyTorch Wheels...")
    if os.path.exists(tar_file_path):
        os.remove(tar_file_path)
    with tarfile.open(tar_file_path, "w:gz") as tar_file:
        for root, dirs, files in os.walk(Paths.ASSETS):
            for file in tqdm(files, desc="Compressing files", unit="files"):
                if not file.endswith(".whl"):
                    continue
                file_path: str = os.path.join(root, file)
                tar_file.add(file_path, arcname=file)
    
    print("\nRemoving PyTorch Wheels...")
    for root, dirs, files in os.walk(Paths.ASSETS):
        for file in tqdm(files, desc="Removing files", unit="files"):
            for dir in tqdm(dirs, desc="Removing dirs", unit="dirs"):
                dir_path: str = os.path.join(root, dir)
                os.rmdir(dir_path)
            file_path: str = os.path.join(root, file)
            if file.endswith("tar.gz"):
                continue
            os.remove(file_path)

def _build_tensorrt_wheel(force_compile: bool) -> None:
    tensorrt_version: str = get_config()[ConfigKeys.TENSORRT_VERSION]
    tar_file_name: str = f"tensorrt{tensorrt_version}-{CYTHON_VERSION}.tar.gz"
    tar_file_path: str = os.path.join(Paths.ASSETS, tar_file_name)
    if not force_compile:
        if _check_asset(tar_file_path):
            return

    print("Building TensorRT Containerfile...")
    compile_tensorrt_original: str = ""
    with open(f"{Containerfiles.COMPILE_TENSORRT}", "r") as compile_tensorrt_file:
        compile_tensorrt_original = compile_tensorrt_file.read()
    with open(f"{Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_TENSORRT}", "w") as compile_tensorrt_file:
        compile_tensorrt: str = compile_tensorrt_original.replace(VariableReferences.CONTAINER_NAME, CONTAINER_NAME)
        compile_tensorrt = compile_tensorrt.replace(VariableReferences.BASE_CONTAINER_TAG, Tags.BASE)
        compile_tensorrt = compile_tensorrt.replace(VariableReferences.TENSORRT_VERSION, get_config()[ConfigKeys.TENSORRT_VERSION])
        compile_tensorrt = compile_tensorrt.replace(VariableReferences.PYTHON_VERSION, get_config()[ConfigKeys.PYTHON_VERSION])
        python_minor_version: str = get_config()[ConfigKeys.PYTHON_VERSION].replace("3.", "")
        compile_tensorrt = compile_tensorrt.replace(VariableReferences.PYTHON_MINOR_VERSION, python_minor_version)
        compile_tensorrt_file.write(compile_tensorrt)
    
    print("Compiling TensorRT Wheel...")
    docker_client: DockerClient = docker.from_env()
    while True:
        try:
            docker_client.images.get(ImageNames.BASE)
            break
        except ImageNotFound:
            sleep(5)
    compile_tensorrt_command: str = f"docker build -t {ImageNames.COMPILE_TENSORRT} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.COMPILE_TENSORRT} ."
    execute(compile_tensorrt_command)

    print("Extracting TensorRT Wheel...")
    while True:
        try:
            docker_client.images.get(ImageNames.COMPILE_TENSORRT)
            break
        except ImageNotFound:
            sleep(5)
    docker_client.containers.run(
        image=ImageNames.COMPILE_TENSORRT,
        volumes={f"{os.getcwd()}/{Paths.ASSETS}": {"bind": "/home/assets", "mode": "rw"}},
        remove=True,
        stdin_open=True,
        tty=True,
        detach=False,
        stdout=True,
        stderr=True
    )

    print("Cleaning up Image...")
    docker_client.images.remove(ImageNames.COMPILE_TENSORRT)
    
    print("Compressing TensorRT Wheel...")
    if os.path.exists(tar_file_path):
        os.remove(tar_file_path)
    with tarfile.open(tar_file_path, "w:gz") as tar_file:
        for root, dirs, files in os.walk(Paths.ASSETS):
            for file in tqdm(files, desc="Compressing files", unit="files"):
                if not file.endswith(".whl") and not file.endswith(".deb"):
                    continue
                file_path: str = os.path.join(root, file)
                tar_file.add(file_path, arcname=file)
    
    print("\nRemoving TensorRT Wheel...")
    for root, dirs, files in os.walk(Paths.ASSETS):
        for file in tqdm(files, desc="Removing files", unit="files"):
            for dir in tqdm(dirs, desc="Removing dirs", unit="dirs"):
                dir_path: str = os.path.join(root, dir)
                os.rmdir(dir_path)
            file_path: str = os.path.join(root, file)
            if file.endswith("tar.gz"):
                continue
            os.remove(file_path)

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
        full_containerfile = full_containerfile.replace(VariableReferences.PYTHON_VERSION, get_config()[ConfigKeys.PYTHON_VERSION])
        full_containerfile = full_containerfile.replace(VariableReferences.CYTHON_VERSION, CYTHON_VERSION)
        full_containerfile = full_containerfile.replace(VariableReferences.OPENCV_VERSION, get_config()[ConfigKeys.OPENCV_VERSION])
        full_containerfile = full_containerfile.replace(VariableReferences.PYTORCH_VERSION, get_config()[ConfigKeys.PYTORCH_VERSION])
        full_containerfile = full_containerfile.replace(VariableReferences.TENSORRT_VERSION, get_config()[ConfigKeys.TENSORRT_VERSION])
        final_file.write(full_containerfile)
    print("Building Full Image...")
    full_container_name: str = f"{CONTAINER_NAME}:{Tags.FULL}"
    build_full_command: str = f"docker build -t {full_container_name} -f {Paths.TEMP_CONTAINERFILES}/{Containerfiles.FULL} ."
    execute(build_full_command)

def cleanup() -> None:
    print("Cleaning up...")
    if os.path.exists(Paths.TEMP_CONTAINERFILES):
        shutil.rmtree(Paths.TEMP_CONTAINERFILES)


# MAIN
def main() -> None:
    print("Starting Compile & Build Process...")
    _setup()
    arguments: dict[str, bool] = _parse_args()
    should_force_compile: bool = arguments[ArgumentNames.FORCE_COMPILE]
    _build_base_image()
    _build_opencv_deb(force_compile=should_force_compile)
    _build_pytorch_wheels(force_compile=should_force_compile)
    _build_tensorrt_wheel(force_compile=should_force_compile)
    _build_final_image()
    cleanup()
    print("\nFull Build Process Completed!\n")

if __name__ == "__main__":
    main()
