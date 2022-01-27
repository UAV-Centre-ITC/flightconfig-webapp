Inference of MultEYE

For Single image

Run 

python yolo.py --model_type=tiny_yolo3_mobilenetv3small_lite --weights_path=test.h5 --anchors_path=configs/tiny_yolo3_anchors.txt --classes_path=configs/voc_classes.txt --model_image_size=512x512 --image

If all goes well, the script will expect an input (location of the image to be processed) like the following:

#######################################################
Image detection mode
 Ignoring remaining command line arguments: ./path2your_video,
Input image filename:/path/to/the/image.jpg
#######################################################

If it runs successfully, it shows something like this

#######################################################
Found 8 boxes for image
Inference time: 2.38601875s
Input image filename:
#######################################################

The script saves the detection (with drawn bounding boxes) and segmentation as detections.jpg and segmentation.jpg in multeye/ (and gets replaced after each run of inference 


For Video 

python yolo.py --model_type=tiny_yolo3_mobilenetv3small_lite --weights_path=test.h5 --anchors_path=configs/tiny_yolo3_anchors.txt --classes_path=configs/voc_classes.txt --model_image_size=512x512 --input='./path2yourVideo' --output='/save/path/of/video.mp4'