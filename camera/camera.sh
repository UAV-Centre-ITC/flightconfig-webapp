#!/bin/bash

cameratime=$1
savedir=$2

python3 ~/Documents/camera/camera.py --time $cameratime --save_dir $savedir

exit 0
