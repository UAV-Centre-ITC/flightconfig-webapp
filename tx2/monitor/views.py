from django.shortcuts import render
from django.http import JsonResponse

import ptpy
from .utils.camerathreading import CameraStart, CameraDownload,  loadVehicleObject
from monitor.tasks import Watchfolder,  WebCamTask,  loadModelObject,  transfer_logs,  reset_index

from configparser import ConfigParser
import time
import os
from datetime import datetime 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import subprocess
import glob

log = logging.getLogger(__name__)

def monitoring_view(request, flightname):
    global cstart
    global cdown
    global watcher
    global webcam
    global modelobject
    global vehicleobject
    global index1,  index2,  index3
    
    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    
    reset_index()
    
    if request.method == "GET":
        
        # Watch for new camera captures
        observer = Watchfolder(category='basic')
        observer.start()
        
        # Instantiate watchfolders/transfers
        choices = {
                '0': 'Original images',
                '1': 'Processed images',
                '2': 'Labels'
                }
                
        transfers = []
        for i in range(len(choices)):
            if config.get('main','t'+str(int(i))) == 'True':
                transfers.append(choices[str(i)])
                observer = Watchfolder(category='t'+str(int(i)))
                observer.start()
        
        if config.get('main',  'model') != 'none':
            # Instantiate deep learning model
            modelobject= None
            modelobject = loadModelObject()
        
        # connect to mavlink vehicle
        loadVehicleObject()
        #run tegrastats
        file = os.path.join(config.get('dirs', 'logdir'), 'tegrastats.txt')
        cmmd=['/home/jetsontx2/Documents/django/tx2/tegrastats.sh', file, '&']
        tr= subprocess.run(cmmd)
        
        return render(request, 'monitor/flight_monitoring.html', {'flightname': config.get('main', 'flightname'), 'camera':config.get('main', 'camera'), 'gcs':config.get('main', 'gcs'), 'model': config.get('main', 'model'), 'transfer': transfers, 'compressed': config.get('main', 'compressed'), 'notes': config.get('main', 'notes')})
    
    elif request.method == 'POST' and request.POST['action_key']:
        if request.POST['action_key'] == 'start_camera':
            if config.get('main',  'camera') == 'PTP-device (SODA)':
                #start camera thread
                camera = ptpy.PTPy()
                cstart = CameraStart(camera)
                cdown = CameraDownload(camera, config.get('dirs', 'sodadir'))
                cstart.start()
                cdown.start()
            elif config.get('main',  'camera') == 'usb-camera':
                webcam = WebCamTask.apply_async([config.get('dirs', 'sodadir')])
            else:
                print('Error')
            return JsonResponse({'action_key':'start_camera'})
            
        elif request.POST['action_key'] == 'stop_camera':   
            if config.get('main',  'camera') == 'PTP-device (SODA)':
                cstart.stopit()
                cstart.join()
            elif config.get('main',  'camera') == 'usb-camera':
                webcam.revoke(terminate=True)
            else:
                print('error')    
            return JsonResponse({'action_key':'stop_camera'})
            
        elif request.POST['action_key'] == 'stop_flight': 
            if config.get('main',  'camera') == 'PTP-device (SODA)':
                #wait for final images to download, use button to shut down processing and transfer final log files. 
                cdown.stopit()
                cdown.join()
                time.sleep(10)
                # send final message to websocket
                now = datetime.now()
                date_time = now.strftime("%H:%M:%S.%f")[:-3]
                mess = '[{}] LOG - Flight finished'.format(date_time)
                message = {'type': 'camera_log_message', 'data':{'transferlogmessage4': mess}}
                log.info(mess)
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)('camera-log', message)
                # transfer final logs
                transfer_logs.apply_async([os.path.join(config.get('dirs',  'logdir'),  'flight.log'),  os.path.join(config.get('dirs',  'logdir'),  'config.ini')])
                # cleanup
                cleanup()
            return JsonResponse({'action_key':'stop_flight'})
            
    else:
        return JsonResponse({'camera_key':False})


def cleanup():
    print("within cleanup")
    # read configs file
    config = ConfigParser()
    config.read('config.ini')
    
    for f in glob.glob(os.path.join(*[config.get('dirs', 'maindir'), '**', '*128x128.jpg']), recursive=True):
        cmmd = ['rm', '-r', f]
        tr = subprocess.run(cmmd)
        
    # remove thumbnail dir
    cmmd = ['rm', '-r', config.get('dirs',  'sodadir_thumb')]
    tr = subprocess.run(cmmd)
    if tr.returncode == 0:
        log.info('thumbnails removed')
