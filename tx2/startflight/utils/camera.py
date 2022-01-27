#!/usr/bin/python
import ptpy
from ptpy.transports.usb import find_usb_cameras
from threading import Thread, Event
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler
from time import sleep, time
import os
import argparse
import sys
from datetime import datetime

# Run Command: python3 camera.py --time 60

# parse the command line
parser = argparse.ArgumentParser(description="Script to trigger camera", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--time", type=int, default=30, help="number of minutes to take images")

try:
	opt, argv = parser.parse_known_args()
except:
	print("")
	parser.print_help()
	sys.exit(0)

# Set up log
log = logging.getLogger('Live')
formatter = logging.Formatter(
	'%(levelname).1s '
	'%(relativeCreated)d '
	'%(name)s'
	'[%(threadName)s] '
	'%(message)s'
)
handler = RainbowLoggingHandler(
    sys.stderr,
)
level = 'INFO'
log.setLevel(level)
handler.setFormatter(formatter)
log.addHandler(handler)

# get datetime
now = datetime.now()
date_time = now.strftime("%d%m%y_%H%M%S")

# Set up directories
cur_dir = os.getcwd()
os.chdir('/home/jetsontx2')
save_dir = os.path.join(*[os.getcwd(), 'Data', 'images', 'SODA_images_{}'.format(date_time)])
print(save_dir)

if not os.path.exists(save_dir):
	os.makedirs(save_dir)

# Set up threads and events
finished = Event()

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
		caminfo = camera.get_device_info()
		while not finished.is_set():
			event = camera.event()
			if event and event.EventCode == 'ObjectAdded':
				print(event.EventCode)
				handle = event.Parameter[0]
				info = camera.get_object_info(handle)
				# Download all things that are not groups of other things.
				if info.ObjectFormat != 'Association':
					if info.Filename[-3:] == 'JPG':
						log.info('{}: save capture {}'.format(caminfo.SerialNumber, info.Filename))
						tic = time()
						obj = camera.get_object(handle)
						toc = time()
						log.info('{}: download speed {:.1f}MB/s'.format(caminfo.SerialNumber, len(obj.Data) / ((toc - tic) * 1e6)))
						save_path = os.path.join(save_dir, info.Filename)
						with open(save_path, mode='wb') as f:
							f.write(obj.Data)


# Find each connected USB camera try to instantiate it and set up a capture.
threads = []
for i, device in enumerate(find_usb_cameras()):

    try:
        camera = ptpy.PTPy(device=device)
        info = camera.get_device_info()
        caminfo = (info.Manufacturer, info.Model, info.SerialNumber)
        if (
                'InitiateCapture' not in info.OperationsSupported or
                'GetObject' not in info.OperationsSupported
        ):
            raise Exception(
                '{} {} {} does not support capture or download...'
                .format(*caminfo)
            )
        log.info(
            'Found {} {} {}'
            .format(*caminfo)
        )
    except Exception as e:
        log.error(e)
        continue

    capture = Thread(
        name='PHOTO{:02}'.format(i),
        target=capture_thread,
        args=(camera,)
    )
    threads.append(capture)

    download = Thread(
        name='DWNLD{:02}'.format(i),
        target=download_thread,
        args=(camera,)
    )
    threads.append(download)

for thread in threads:
    thread.start()

# Let the threads run for amount of time
sleep(opt.time*60) # multiply by seconds per minutes
finished.set()

# Wait for threads to finish running.
for thread in threads:
    if thread.is_alive():
        thread.join()
