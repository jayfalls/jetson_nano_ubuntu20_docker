<h1 align="center">🐳 Jetson Nano Ubuntu 20.04 Docker Images 🐳</h1>

## What is this?

Hardware accelerated OpenCV, Torch & Tensorrt Ubuntu 20.04 docker images for Jetson Nano containing any python version you need up until the latest 3.12

## Pulling existing images

| Python Version | Dockerhub Image Name             | Size     |
|----------------|----------------------------------|----------|
| `Python3.12`   | `jayfalls/l4t-20.04:base-cu312`  | Unkwnown |
| `Python3.12`   | `jayfalls/l4t-20.04:full-cu312`  | Unkwnown |
| `Python3.11`   | `jayfalls/l4t-20.04:base-cu311`  | 65.7MB   |
| `Python3.11`   | `jayfalls/l4t-20.04:full-cu311`  | 4.74GB   |
| `Python3.10`   | `jayfalls/l4t-20.04:base-cu310`  | Unkwnown |
| `Python3.10`   | `jayfalls/l4t-20.04:full-cu310`  | Unkwnown |
| `Python3.9`    | `jayfalls/l4t-20.04:base-cu39`   | Unkwnown |
| `Python3.9`    | `jayfalls/l4t-20.04:full-cu39`   | Unkwnown |
| `Python3.8`    | `jayfalls/l4t-20.04:base-cu38`   | Unkwnown |
| `Python3.8`    | `jayfalls/l4t-20.04:full-cu38`   | Unkwnown |

>  **note:** make sure to run the container on the latest L4T host system (r32.7.1). Running on older JetPack releases (e.g. r32.6.1) can cause driver issues, since L4T drivers are passed into the container.

## If an image with your desired python version doesn't exist in the docker hub, or you are running an older jetpack release, or you are running a different board (e.g. AGX/NX Xavier), then you'll need to build it manually

[Building Ubuntu 20.04 Images with Custom Python Versions](./documentation/building_manually.md)

## Contributing

You can contribute in the following ways

- [Create an issue](https://github.com/jayfalls/jetson-nano-ubuntu20-docker/issues/new)
- [Open a Pull request](https://github.com/jayfalls/jetson-nano-ubuntu20-docker/pulls)
- [Request to Upload New Images](./documentation/building_manually.md#New-images)

>  **note:** I do not have a lot of free time, so I'm not sure if I'll support this fully, as such don't expect too much from me please. The [license](./LICENSE) is MIT, so you can continue it on your own repo if I don't support.

## References

- [Jetson Nano Ubuntu20.04](https://github.com/timongentzsch/Jetson_Ubuntu20_Images)
- [Building OpenCV](https://qengineering.eu/install-opencv-on-jetson-nano.html)
- [Building Pytorch](https://qengineering.eu/install-pytorch-on-jetson-nano.html)
- [Jetson Nano Ubuntu20.04 Docker Images](https://github.com/timongentzsch/Jetson_Ubuntu20_Images)
