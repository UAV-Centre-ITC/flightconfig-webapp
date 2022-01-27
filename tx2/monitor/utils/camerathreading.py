import time
import threading
import os
from datetime import datetime
import subprocess
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dronekit import connect
import dronekit

import logging
log = logging.getLogger(__name__)

global vehicleobject

def loadVehicleObject():
    global vehicleobject
    try:
        vehicleobject = connect("0.0.0.0:14550", wait_ready=True)
        print("Mavlink: connection to vehicle succeeded")
    except dronekit.APIException as e:
        print("Mavlink: connection to vehicle failed")
        vehicleobject = None        

def getCoords(vehicleobject):
    vehicle=vehicleobject
    
    if vehicle is None:
        lat = None
        lon = None
        alt = None
    else:
        lat = vehicle.location.global_frame.lat
        lon = vehicle.location.global_frame.lon
        alt = vehicle.location.global_frame.alt
    return lat,  lon,  alt

class StoppableThread(threading.Thread):

	# Thread class with a _stop() method.
	# The thread itself has to check
	# regularly for the stopped() condition.

	def __init__(self, *args, **kwargs):
		super(StoppableThread, self).__init__()
		self._stopper = threading.Event()

	# function using _stop function
	def stopit(self):
		self._stopper.set()

	def stopped(self):
		return self._stopper.is_set()


class CameraStart(StoppableThread):

	import time

	def __init__(self, camera):
	  StoppableThread.__init__(self)
	  self.camera = camera

	def run(self):
		print( "START: thread running")
		with self.camera.session():
			self.camera.get_device_info()
			while not self.stopped():
				self.camera.initiate_capture()
			print( "START: thread ending")

class CameraDownload(StoppableThread):
    import time
    global vehicleobject
    
    def __init__(self, camera, savedir):
        StoppableThread.__init__(self)
        self.camera = camera
        self.savedir = savedir

    def run(self):
        print( "DWN: thread running")
        with self.camera.session():
            while not self.stopped():
                event = self.camera.event()
                if event and event.EventCode == 'ObjectAdded':
                    handle = event.Parameter[0]
                    info = self.camera.get_object_info(handle)
                    # Download all things that are not groups of other things.
                    if info.ObjectFormat != 'Association':
                        obj = self.camera.get_object(handle)
                        with open(os.path.join(self.savedir, info.Filename), mode='wb') as f:
                            f.write(obj.Data)
                        # Send message to socket    
                        now = datetime.now()
                        date_time = now.strftime("%H:%M:%S.%f")[:-3]
                        lat,  lon,  alt = getCoords(vehicleobject)
                        cap_mess = "[{}] Captured {}, lat={}, lon={}, alt={}".format(date_time, info.Filename,  lat,  lon,  alt)
                        message = {'type': 'camera_log_message', 'data':{'cameralogmessage': str(cap_mess)}}
                        log.info(cap_mess)
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)('camera-log', message)
            print( "DWN: thread ending")


class WebcamStart(StoppableThread):
	def __init__(self, savedir):
	  StoppableThread.__init__(self)
	  self.savedir = savedir
	  print( "START: webcam init")

	def run(self):
		print( "START: webcam thread running")
		while not self.stopped():
			now = datetime.now()
			date_time = now.strftime("%d%m%y_%H%M%S")
			filepath = os.path.join(self.savedir, "{}.jpg".format(date_time))
			
			cmmd = ["fswebcam", "-r", "1280x720", "--no-banner", filepath]
			list_files = subprocess.run(cmmd)
			
			time.sleep(1)
			
			if list_files.returncode == 0:
				print('{}: successfully initiated capture'.format(filepath))

			print( "START: thread ending")
