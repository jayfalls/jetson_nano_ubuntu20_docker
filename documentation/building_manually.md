## [:arrow_up_small:](..)

# Building Ubuntu 20.04 Container Images Manually

## Preparing Python

This works differently for different distributions

### Ubuntu 18.04

```shell
sudo su
apt update
apt install -y software-properties-common build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libfreetype6-dev libopenblas-base libopenmpi-dev libjpeg-dev zlib1g-dev
wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz
tar -xf Python-3.11.8.tgz
cd Python-3.11.8
./configure --enable-optimizations
make -j 4
make altinstall
update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1
update-alternatives --config python3
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
python3 -m ensurepip --upgrade
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
apt-get install -y python3-venv binfmt-support python3-libnvinfer python3-libnvinfer-dev
```

### Ubuntu 20.04

```shell
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get install -y python3.11
apt-get install -y python3.11-full python3.11-dev python3-numpy
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
update-alternatives --config python3
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
ln -sf /usr/bin/python3 /usr/bin/python
apt install python3-pip -y
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
python3 -m pip install --upgrade pip
```

## Prepering the Device

- Temporarily enable Swap on your Jetson Nano
```shell
apt-get install -y dphys-swapfile
```
  
- Edit the main swap config
```shell
vi /sbin/dphys-swapfile
```
  
- Change the defaults to this
```plaintext
CONF_SWAPFILE=/path/to/swap # You can jump to this line by pressing the keys 16G
CONF_MAX_SWAP=4096 # You can jump to this line by pressing the keys 30G
```
  
- Then the user config
```shell
bash -c 'cat > /etc/dphys-swapfile' << EOF
CONF_SWAPFILE=/path/to/swap
CONF_MAX_SWAP=4096
EOF
```
  
- Generate the swap file
```shell
dd if=/dev/zero of=/path/to/swap bs=1M count=4096
mkswap /path/to/swap
```
  
- Start the swap
```shell
systemctl restart dphys-swapfile
```
  
- Verify the swap with
```shell
free -m
```
The Swap should be something like `6077`

- Enable nvcc in path
```shell
sudo ln -s /usr/local/cuda/bin/nvcc /usr/bin/nvcc
```
  
- Link cublas
```shell
ln -s /usr/local/cuda/lib64/libcublas.so /usr/lib/aarch64-linux-gnu/libcublas.so
```
  
- Install remaining Jetpack files
```shell
sudo apt-get update && sudo apt-get install nvidia-jetpack
```

## Overclocking for faster compile speeds

**WARNING! You need to attach a fan to the device if you are doing this, I am not responsible for any damage to your device if you do this step...**
- [Overclocking Jetson Nano](https://qengineering.eu/overclocking-the-jetson-nano.html)

## Installing Dependencies

- Install dependencies
```shell
git clone https://github.com/jayfalls/jetson_nano_ubuntu20_docker
cd jetson_nano_ubuntu20_docker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements
```

- Download [Deepstream 6.0.1](https://developer.nvidia.com/deepstream_sdk_v6.0.1_jetsontbz2) & [RTSP Stream Patch](https://developer.nvidia.com/libgstvideo-10so014050)
>  **note:** You will need to have an NVONLINE account which you can register, and then request dev access if you don't already have. Don't worry, it's basically instant once you request. Download through a browser and then find a way to get this file into the `jetson_nano_ubuntu20_docker` folder before building

## Configuration
- Edit the `config` file to update the python version you want the container to use
>  **note:** Do not change the anything but the python version, everything else is already the latest that jetson nano supports, and torch builds will break if you change the version, unless you create new patches for it, refer to [line 59](../Containerfile.compile_torch#59) for more details
>  **note:** Only Python versions after 3.10 are directly supported by this repo, but you can add support for older versions by creating a new patch file for torch, and adding it to the `patches` folder, and then updating the `config` file to use the lower torch version, refer to building pytorch in the [References](../README.md#references) for more details on how to create your own patches, just apply the changes and run `git diff` and copy the whole diff into a patch with the corresponding name and torch version. It might just work without doing this, but I haven't tested...

## Compiling & Building
**The Compile & Build Steps can take up to 18 hours! Make sure you have at least 17gb free and you can leave the device on during this time, have patience...**
**If you don't want to compile some steps or would like to use the opencv, torch, tensorrt somewhere else, you can download the precompiled images [here](https://drive.google.com/drive/folders/1z-CX_9vtfsWeC0SQjalxAdMIZQgQDs2H?usp=drive_link). Just make sure you get the files that match your python version**

- There are two ways of compiling & building
1. If you are using the desktop, open a terminal and run
```shell
./build.py
```

2. If you are ssh'd in
```shell
nohup python3 build.py > build.log 2>&1 &
```
You can leave the process running, and if you ever want to check on progress you ssh back, cd into this directory and run
```shell
tail -fn 25 build.log
```

- The process is done once you see `Full Build Process Completed!`

## Cleaning up

- Delete the repo

- Restore original python version
```shell
update-alternatives --config python3
```

- Disable the swap
```shell
systemctl stop dphys-swapfile
rm /path/to/swap
```

- Underclock if you plan on using this device without a fan
