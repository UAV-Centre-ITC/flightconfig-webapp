import time
import threading
import ptpy

def capture_thread(camera):
	'''Initiate captures regularly for camera'''
	with camera.session():
		info = camera.get_device_info()
		while not finished.is_set():
			capture = camera.initiate_capture()
			if capture.ResponseCode == 'OK':
				log.info('{}: successfully initiated capture'.format(info.SerialNumber))

def download_thread(camera):
	'''Download all non-folders in events from camera'''
	with camera.session():
		while not finished.is_set():
			event = camera.event()
			if event and event.EventCode == 'ObjectAdded':
				handle = event.Parameter[0]
				info = camera.get_object_info(handle)
				# Download all things that are not groups of other things.
				if info.ObjectFormat != 'Association':
					obj = camera.get_object(handle)
					# save_path = os.path.join(save_dir, info.Filename)
					print(info.Filename)
					with open(info.Filename, mode='wb') as f:
						f.write(obj.Data)



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
	  print( "START: thread init")

	def run(self):
		print( "START: thread running")
		with camera.session():
			info = camera.get_device_info()
			while not self.stopped():
				capture = camera.initiate_capture()
				if capture.ResponseCode == 'OK':
					print('{}: successfully initiated capture'.format(info.SerialNumber))

			print( "START: thread ending")

class CameraDownload(StoppableThread):

	import time

	def __init__(self, camera):
	  StoppableThread.__init__(self)
	  print("DWN: thread init")

	def run(self):
		print( "DWN: thread running")
		with camera.session():
			while not self.stopped():
				event = camera.event()
				if event and event.EventCode == 'ObjectAdded':
					handle = event.Parameter[0]
					info = camera.get_object_info(handle)
					# Download all things that are not groups of other things.
					if info.ObjectFormat != 'Association':
						obj = camera.get_object(handle)
						# save_path = os.path.join(save_dir, info.Filename)
						print('{}: succesfully downloaded capture'.format(info.Filename))
						with open(info.Filename, mode='wb') as f:
							f.write(obj.Data)
			print( "DWN: thread ending")


# camera = ptpy.PTPy()
#
# cstart = CameraStart(camera)
# cdown = CameraDownload(camera)
#
# cstart.start()
# cdown.start()
#
# time.sleep(10)
#
# print("stopping thread")
# cstart.stopit()                                      #  (avoid confusion)
# cdown.stopit()
#
# print("waiting for thread to finish")
# cstart.join()
# cdown.join()
