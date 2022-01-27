from celery import shared_task
import time
import os
from datetime import datetime
import subprocess
from PIL import ImageFile, Image

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from configparser import ConfigParser
import json
import logging
log = logging.getLogger(__name__)

ImageFile.LOAD_TRUNCATED_IMAGES = True

def WebCam(savedir):
	# initiate webcame image capture	
	now = datetime.now()
	date_time = now.strftime("%d%m%y_%H%M%S")
	file_name = "{}.jpg".format(date_time)
	filepath = os.path.join(savedir, file_name)
	cmmd = ["fswebcam", "-r", "1280x720", "--no-banner", filepath]
	subprocess.run(cmmd)
	#if list_files.returncode == 0:
		#print('{}: successfully initiated capture'.format(filepath))
	return "Successfully captured {}".format(file_name)

@shared_task
def WebCamTask(savedir):
	while True:
		webcam_message = WebCam(savedir)
		message = {'type': 'camera_log_message', 'data':{'cameralogmessage': str(webcam_message)}}
		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)('camera-log', message)
		time.sleep(1)

@shared_task
def Watchfolder(category='basic'):
    # http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/

    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    if category == 'basic':
        # apply deep learning
        go_recursively = False
        patterns = ["*"]
        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_created = on_created
        path = config.get('dirs',  'sodadir')
    elif category == 't0':
        # transfer originals
        go_recursively = False
        if config.get('main', 'compressed') =='yes':
            patterns = ["*128x128.JPG"]
            path = config.get('dirs', 'sodadir_thumb')
        else:
            patterns = ["*.JPG"]
            path = config.get('dirs', 'sodadir')
        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_created = on_created_transfer
        
    elif category == 't1':
        # transfer images
        go_recursively = True
        if config.get('main', 'compressed') =='yes':
            patterns = ["*_obj_128x128.jpg",  '*_seg_128x128.jpg']
        else:
            patterns = ["*_obj.jpg",  '*_seg.jpg']
        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_created = on_created_transfer
        path = config.get('dirs', 'maindir')
    elif category == 't2':
        # transfer labels
        go_recursively = False
        patterns = ["*.json"]
        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_created = on_created_transfer
        path = config.get('dirs', 'detectiondir')

    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    
    return my_observer

#TODO globals should not be used in django/celery. Is there a better method?
global modelobject

@shared_task
def loadModelObject():
    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    model = config.get('main', 'model')
    
    if model == 'MultEYE (object)':
        from monitor.utils.models import instantiateYolo
        global modelobject
        modelobject = instantiateYolo()
        # warmup
        image = Image.open('static/SODA0097.JPG').convert('RGB')
        modelobject.detect_image(image)
    #TODO: implement other models
    return modelobject

@shared_task
def on_created(event):
    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    model = config.get('main', 'model')
    
    # make thumbnails
    make_thumbnails.apply_async([event.src_path, config.get('dirs','sodadir_thumb'),  'original'])
    
    if model == 'MultEYE (object)':
        execute_MultEYE_obj(event.src_path)
    elif model == 'MultEYE (segmentation)':
        execute_MultEYE_seg(event.src_path)

@shared_task
def on_created_transfer(event):
    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    
    file_path = event.src_path
    path_split = os.path.join(*file_path.split('/')[-4:])
    
    if 'SODA_images' in path_split:
        cat = 'ORIGINAL'
        if config.get('main', 'gcs') == 'FTP-server':
            cmmd = ["monitor/utils/transfer_to_rmt_dirs.sh",  config.get('rmt', 'sodadir'),  path_split] 
        else:
            cmmd = ['rsync', '-a', '--relative', path_split, config.get('network', 'address') +':~/Documents/']
    elif 'segmentations' in path_split:
        cat = 'SEGMENTATION'
        if config.get('main', 'gcs') == 'FTP-server':
            cmmd = ["monitor/utils/transfer_to_rmt_dirs.sh",  config.get('rmt', 'segmentationdir'),  path_split]
        else:
            cmmd = ['rsync', '-a', '--relative', path_split, config.get('network', 'address') +':~/Documents/']
    elif 'detections' in path_split:
        cat = 'DETECTIONS'
        if config.get('main', 'gcs') == 'FTP-server':
            cmmd = ["monitor/utils/transfer_to_rmt_dirs.sh",  config.get('rmt', 'detectiondir'),  path_split]
        else:
            cmmd = ['rsync', '-a', '--relative', path_split, config.get('network', 'address') +':~/Documents/']
    
    start = time.time()
    tr = subprocess.run(cmmd)
    end = time.time()
    
    if tr.returncode == 0:
        now = datetime.now()
        date_time = now.strftime("%H:%M:%S.%f")[:-3]
        mess = '[{}] {} - Transferred {} in {}s'.format(date_time,  cat,  file_path.split('/')[-1:][0],  round(end-start,  3))
        message = {'type': 'camera_log_message', 'data':{'transferlogmessage1': mess}}
        log.info(mess)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('camera-log', message)
    
@shared_task
def transfer_logs(log_path,  config_path):
    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    
    # transfer log
    path_split = os.path.join(*log_path.split('/')[-4:])
    if config.get('main',  'gcs') =='FTP-server':
        cmmd = ["monitor/utils/transfer_to_rmt_dirs.sh",  config.get('rmt', 'logdir'),  path_split]
    else:
        cmmd = ['rsync', '-a', '--relative', path_split, config.get('network', 'address') +':~/Documents/']
    start = time.time()
    tr = subprocess.run(cmmd)
    end = time.time()
    
    if tr.returncode == 0:
        now = datetime.now()
        date_time = now.strftime("%H:%M:%S.%f")[:-3]
        mess = '[{}] {} - Transferred {} in {}s'.format(date_time,  'LOG',  log_path.split('/')[-1:][0],  round(end-start,  3))
        message = {'type': 'camera_log_message', 'data':{'transferlogmessage5': mess}}
        log.info(mess)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('camera-log', message)
        
    #transfer_config
    path_split = os.path.join(*config_path.split('/')[-4:])
    #cmmd = ['rsync', '-a', '--relative', path_split, config.get('network', 'address') +':~/Documents/']
    cmmd = ["monitor/utils/transfer_to_rmt_dirs.sh",  config.get('rmt', 'logdir'),  path_split]
    start = time.time()
    tr = subprocess.run(cmmd)
    end = time.time()
    
    if tr.returncode == 0:
        now = datetime.now()
        date_time = now.strftime("%H:%M:%S.%f")[:-3]
        mess = '[{}] {} - Transferred {} in {}s'.format(date_time,  'LOG',  config_path.split('/')[-1:][0],  round(end-start,  3))
        message = {'type': 'camera_log_message', 'data':{'transferlogmessage6': mess}}
        log.info(mess)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('camera-log', message)
        
    #transfer_tegrastats
    tegrapath = os.path.join(config.get('dirs', 'logdir'), 'tegrastats.txt')
    path_split = os.path.join(*tegrapath('/')[-4:])
    
    #stop tegrastats
    cmmd = ["tegrastats",  "--stop"]
    tr = subprocess.run(cmmd)
    if tr.returncode == 0:
        print('stopped tegrastats')
    #cmmd = ['rsync', '-a', '--relative', path_split, config.get('network', 'address') +':~/Documents/']
    cmmd = ["monitor/utils/transfer_to_rmt_dirs.sh",  config.get('rmt', 'logdir'),  path_split]
    start = time.time()
    tr = subprocess.run(cmmd)
    end = time.time()
    
    if tr.returncode == 0:
        now = datetime.now()
        date_time = now.strftime("%H:%M:%S.%f")[:-3]
        mess = '[{}] {} - Transferred {} in {}s'.format(date_time,  'LOG',  tegrapath.split('/')[-1:][0],  round(end-start,  3))
        message = {'type': 'camera_log_message', 'data':{'transferlogmessage7': mess}}
        log.info(mess)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('camera-log', message)
    
    
def execute_MultEYE_obj(file_path):
    global modelobject

    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    
    succes = True
    for r in range(2):
        try:
            image = Image.open(file_path).convert('RGB')
        except IOError as e:
            succes=False
            if r == 1:
                print('breaking')
                break
                
    if succes:
        seconds, boxes, classes,  r_img, class_namezs,  s_img= modelobject.detect_image(image)
        image.close()

        nr_box = len(boxes)
        # if detection, do following:
        #if nr_box > 0:
        if nr_box > 0:
            # send message to broker
            now = datetime.now()
            date_time = now.strftime("%H:%M:%S.%f")[:-3]
            if len(classes)>0:
                mess = '[{}] {} - Found {} objects {} in {}s'.format(date_time,  file_path.split('/')[-1:][0], nr_box,  list(set(classes)),  round(seconds, 3))
                message = {'type': 'camera_log_message', 'data':{'processinglogmessage': mess}}
                log.info(mess)
            else:
                mess = '[{}] {} - Found {} objects in {}s'.format(date_time,  file_path.split('/')[-1:][0], nr_box,  round(seconds,  3))
                message = {'type': 'camera_log_message', 'data':{'processinglogmessage': mess}}
                log.info(mess)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('camera-log', message)

            # set new file names
            new_name = file_path.split('/')[-1:][0][:-4] + '_obj' +'.jpg'
            obj_name = os.path.join(config.get('dirs', 'detectiondir'), new_name)
            new_name = file_path.split('/')[-1:][0][:-4] + '_obj' +'.json'
            json_name = os.path.join(config.get('dirs', 'detectiondir'), new_name)
            new_name = file_path.split('/')[-1:][0][:-4] + '_seg' +'.jpg'
            seg_name = os.path.join(config.get('dirs', 'segmentationdir'), new_name)

            # save detection/segmentation image 
            r_img.save(obj_name)
            s_img.save(seg_name)	

            # create thumbnail and display to websocket with dummy function
            make_thumbnails.apply_async([obj_name, config.get('dirs', 'detectiondir'), 'detection'])
            make_thumbnails.apply_async([seg_name, config.get('dirs', 'segmentationdir'),  'segmentation'])
            
            # save labels as json
            # TODO add gps coordinates
            base,  tail = os.path.split(file_path)
            label = {}
            label[tail] = {}
            
            for i in range(len(boxes)):
                if classes[i] in label[tail]:
                    label[tail][classes[i]].append([int(b) for b in boxes[i]])
                else:
                    label[tail][classes[i]] = []
                    label[tail][classes[i]].append([int(b) for b in boxes[i]])
            
            with open(json_name, 'w') as fp:
                json.dump(label, fp)
        else:
            now = datetime.now()
            date_time = now.strftime("%H:%M:%S.%f")[:-3]
            mess = '[{}] {} - No objects found in {}s'.format(date_time,  file_path.split('/')[-1:][0], round(seconds,  3))
            message = {'type': 'camera_log_message', 'data':{'processinglogmessage': mess}}
            log.info(mess)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('camera-log', message)

@shared_task
def execute_MultEYE_seg(yolo, file_path):
    print("MultEYE segmentation not implemented yet")

global index1
global index2
global index3

index1 = 1
index2 = 1
index3 = 1

def reset_index():
    global index1
    global index2
    global index3

    index1 = 1
    index2 = 1
    index3 = 1
        
def set_i(x):
	x += 1
	if x > 5:
		x = 1
	return x


@shared_task
def make_thumbnails(file_path, savedir,  category='original'):
    path, file = os.path.split(file_path)
    file_name, ext = os.path.splitext(file)
    w = 128
    h = 128
    path_splitted = path.split("/")
        
    succes = True

    for r in range(2):
        try:
            img = Image.open(file_path).convert('RGB')
            img_copy = img.copy()
            img_copy.thumbnail((w, h))
            thumbnail_file = '{}_{}x{}{}'.format(file_name, w, h, ext)
            img_copy.save(os.path.join(savedir, thumbnail_file))
            imagedata = os.path.join(*[path_splitted[-2], savedir.split('/')[-1], thumbnail_file])
            
            img.close()
            img_copy.close()
        except IOError as e:
            succes=False
            if r == 1:
                print('breaking')
                break
                
    if succes:        
        if category == 'original':
            base = 'thumb'
            global index1
            key = base + str(int(index1))
            index1 = set_i(index1)
            print('index1',  index1)
        elif category == 'segmentation':
            base = 'seg_thumb'
            global index2
            key = base + str(int(index2))
            index2 = set_i(index2)
            print('index2',  index2)
        elif category == 'detection':
            base = 'obj_thumb'
            global index3
            key = base + str(int(index3))
            index3 = set_i(index3)
            print('index3',  index3)
            
        message = {'type': 'camera_log_message', 'data':{key: imagedata, key+'_t':file_name}}
        #message = {'type': 'camera_log_message', 'data':{key+'_t':file_name}}        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('camera-log', message)
