from dronekit import connect, VehicleMode
import dronekit
import time

# http://python.dronekit.io/
# not all features are compatible with px4, please test with simulator

def conncectVehicle():
    try:
        vehicle = connect("0.0.0.0:14550", wait_ready=False)
        print("Mavlink: connection to vehicle succeeded")
    except dronekit.APIException as e:
        print("Mavlink: connection to vehicle failed")
        vehicle = None        
    return vehicle
