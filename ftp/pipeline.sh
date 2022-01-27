#!/bin/bash

# At start flight: (optional) ask for flight name, (optional) ask for camera time, (optional) name of deep learning model, (optional) name of variable to transfer
while getopts f:t:m:v: flag
do
    case "${flag}" in
        f) flightname=${OPTARG};;
        t) cameratime=${OPTARG};;
        m) model=${OPTARG};;
        v) variable=${OPTARG};;
    esac
done

echo "flightname: $flightname"
echo "cameratime: $cameratime"
echo "model: $model"
echo "variable to transfer: $variable"

# create project tree:
# flight name
	# SODA_images
	# (optional: if deep learning) object detections
	# (optional: if deep learning) segmentations
	# (optional: if deep learning) labels
	# gps

# store cameratime
if [[ $cameratime = '' ]];then
    declare -i cameratime=1
fi

# create dirname
datetime=$(date +"%d%m%y_%H%M")
if [[ $flightname = '' ]]; then
    dirname=flight_$datetime;
else
    dirname=$flightname;
fi

#dirname=flight_051120
basedir=~/Data/flights/$dirname
sodadir=$basedir/"SODA_images"
gpsdir=$basedir/"gps"
logdir=$basedir/"logs"

pubdir=/pub/DeltaQuad/$dirname
sodadir2=$pubdir/"SODA_images"
gpsdir2=$pubdir/"gps"
logdir2=$pubdir/"logs"

#make dirs on jetson and ftp sever
mkdir "$basedir" "$sodadir" "$gpsdir" "$logdir"
lftp -e "mkdir -p '$pubdir' '$sodadir2' '$gpsdir2' '$logdir2'; bye" ftp.itc.nl

# if deep learning, make other dirs on jetson and ftp server
if [[ ! $model = '' ]]; then
    segdir=$basedir/"segmentations"
    objdir=$basedir/"object_detections"
    labdir=$basedir/"labels"
    segdir2=$pubdir/"segmentations"
    objdir2=$pubdir/"object_detections"
    labdir2=$pubdir/"labels"

    lftp -e "mkdir -p '$segdir2' '$objdir2' '$labdir2'; bye" ftp.itc.nl
    mkdir "$segdir" "$objdir" "$labdir"
fi

# specify dir to monitor and to transfer
if [[ $variable = 'objects' ]]; then
    monitordir=$objdir
    destdir=$objdir2;
elif [[ $variable = 'segmentations' ]]; then
    monitordir=$segdir
    destdir=$segdir2;
elif [[ $variable = 'labels' ]]; then
    monitordir=$labdir
    destdir=$labdir2;
else
    monitordir=$sodadir
    destdir=$sodadir2;
fi

echo "dir to monitor is $monitordir, destination dir is $destdir"
echo "images to process located in $sodadir"
# start watch script monitor_transfer.sh & start camera script $ start deep learning script

if [[ ! $model = '' ]]; then
    ((tegrastats --interval 2000 --logfile $logdir/tegrastats.txt | ts '["%d%m%y_%H%M%.S"]') & (~/Documents/ftp/monitor_transfer.sh $monitordir $destdir | ts '["%d%m%y_%H%M%.S"]') & (~/Documents/camera/camera.sh $cameratime $sodadir | ts '["%d%m%y_%H%M%.S"]') & (~/Documents/models/multeye/run.sh $sodadir $objdir $segdir | ts '["%d%m%y_%H%M%.S"]')) 2>&1 | tee $basedir/$dirname.txt;
else
    tegrastats --interval 2000 --logfile $logdir/tegrastats.txt & ~/Documents/ftp/monitor_transfer.sh $monitordir $destdir & ~/Documents/camera/camera.sh $cameratime $sodadir;
fi

# for testing purposes
#~/Documents/ftp/monitor_transfer.sh $monitordir $destdir & ~/Documents/models/multeye/run.sh $sodadir $objdir $segdir

# if camera script ended OR if cancel, kill all processes and sub-processes





