#!/bin/bash
datetime=$(date +"%d%m%y_%H%M")
dirname=flight_$datetime

(python3 ~/Documents/gps/mavlink-example.py | ts '["%d%m%y_%H%M%.S"]') 2>&1 | tee ~/Documents/gps/$dirname.txt

exit 0
