<h1 align="center">🐳 Jetson Nano Ubuntu 20.04 Docker Images 🐳</h1>

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
CONF_SWAPFILE=/home/lytehouse/sdcard/swap # You can jump to this line by pressing the keys 16G
CONF_MAX_SWAP=4096 # You can jump to this line by pressing the keys 30G
```
  
- Then the user config
```shell
bash -c 'cat > /etc/dphys-swapfile' << EOF
CONF_SWAPFILE=/home/lytehouse/sdcard/swap
CONF_MAX_SWAP=4096
EOF
```
  
- Generate the swap file
```shell
dd if=/dev/zero of=/home/lytehouse/sdcard/swap bs=1M count=4096
mkswap /home/lytehouse/sdcard/swap
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


## Building docker Images

- Edit the config file if you want to update the python version and then run
```shell
cd ~/lytehouse/sdcard
git clone https://github.com/jayfalls/jetson_nano_ubuntu20_docker
cd jetson_nano_20.04_containers
python3 -m venv venv
source venv/bin/activate
pip install -r requirements
./build.py
```

## Cleaning up


## References

- [Original Repo](https://github.com/timongentzsch/Jetson_Ubuntu20_Images)
- [Building OpenCV](https://qengineering.eu/install-opencv-on-jetson-nano.html)
- [Building Pytorch](https://qengineering.eu/install-pytorch-on-jetson-nano.html)