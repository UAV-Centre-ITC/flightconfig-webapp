from dronekit import connect, VehicleMode
import time

# http://python.dronekit.io/
# not all features are compatible with px4, please test with simulator

vehicle = connect("0.0.0.0:14550", wait_ready=False)

while True:
	#print("Global Location: {}".format(vehicle.location.global_frame.lat))
	print(vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_frame.alt)
	time.sleep(1)
