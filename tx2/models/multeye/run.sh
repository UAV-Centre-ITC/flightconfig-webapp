#!/bin/bash

# set environment
activate () {
    ./home/jetsontx2/Documents/models/multeye/multeyevenv/bin/activate
}

cd ~/Documents/models/multeye

python yolo.py --model_type=tiny_yolo3_mobilenetv3small_lite --weights_path=test.h5 --anchors_path=configs/tiny_yolo3_anchors.txt --classes_path=configs/voc_classes.txt --model_image_size=512x512 --imgdir $1 --objdir $2 --segdir $3 --image
