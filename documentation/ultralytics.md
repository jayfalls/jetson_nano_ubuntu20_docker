## [:arrow_up_small:](..)

# Using Ultralytics Yolo Models with Tensorrt

## Converting the model to onnx

- Open this [colab](../yolo/jetson_nano_yolo_onnx_converter.ipynb) notebook in google colab or in vs code on your local machine with a GPU

- Download and convert the models you want, you can move them into your drive and download them to your jetson nano either using gdown or gui if you have

## Converting the model to tensorrt

- Clone this repo onto your jetson nano and go to the yolo folder
```shell
git clone https://github.com/jayfalls/jetson_nano_ubuntu20_docker
cd jetson_nano_ubuntu20_docker/yolo
```

- Download your .onnx model into the yolo folder

- Run this command
```shell
docker run -dit --name tensorrt_conversion -v "${pwd}":/root jayfalls/l4t-20.04:full-cp311 tail -fn 25 /dev/null
docker exec -it tensorrt_conversion bash
```

- If you are trying to convert a yolov10 model, make sure to run the following command first before making the conversion
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements
./v10_fixer.py
```

- Then finally run the tensorrt conversion command
```shell
trtexec --onnx=<yolo>.onnx --saveEngine=<yolo>.engine --fp16
```

You can also try the int8 conversion, but you need to make sure to have a folder `calibration_images` filled with over 500 images similiar to what you are going to be running through your model, try to make them as varied as possible. But this usually gives a very small performance improvement on the jetson nano
```shell
pip install pycuda
wget https://raw.githubusercontent.com/NVIDIA/TensorRT/release/8.2/samples/python/efficientdet/build_engine.py -O build_engine.py
wget https://raw.githubusercontent.com/NVIDIA/TensorRT/release/8.2/samples/python/efficientdet/image_batcher.py -O image_batcher.py
```
```shell
python3 build_engine.py \
    --onnx yolov8n.onnx \
    --engine yolov8n_8.engine \
    --precision int8 \
    --calib_input calibration_images \
    --calib_cache yolov8n_calibration.cache
```


- Run this to leave and delete the docker container you just made
```shell
exit
```
```shell
docker stop tensorrt_conversion && docker rm tensorrt_conversion
```

- Your .engine file should be in the yolo folder that you are currently in
```shell
ls
```

## That's it, you can now use this .engine file with ultralytics or trtexec!
