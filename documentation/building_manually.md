## [:arrow_up_small:](..)

# Building Ubuntu 20.04 Container Images Manually

## Preperation

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

## Overclocking for faster compile speeds

### **WARNING! You need to attach a fan to the device if you are doing this, I am not responsible for any damage to your device if you do this step...**

## Building docker Images

- Edit the `config` file to update the python version you want the container to use

- Install dependencies
```shell
git clone https://github.com/jayfalls/jetson_nano_ubuntu20_docker
cd jetson_nano_ubuntu20_docker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements
```

**The Compile & Build Steps can take up to 12 hours! Make sure you can leave the device on during this time and have patience...**

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

## New images

- Please submit

## Cleaning up

- Delete the repo

- Disable the swap

- Underclock if you plan on using this device without a fan
