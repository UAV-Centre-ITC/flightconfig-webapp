#!/bin/bash

TIMEFORMAT=%R

#MONITORDIR="/home/jetsontx2/Data/images"
MONITORDIR=$1
echo "DIR TO MONITOR IS:" $MONITORDIR
RMTDIR=$2
echo "DIR TO SEND IMAGES TO IS:" $RMTDIR

inotifywait -m -r "${MONITORDIR}" -e create|
    while read dir action file; do
        echo "The file '$file' appeared in directory '$dir'via '$action'"
        if [ $action == "CREATE" ]; then
            echo "Transfering file $file to $RMTDIR"
            time lftp -e "put -O "$RMTDIR/" "$MONITORDIR/$file" ; bye" ftp.itc.nl
            echo "Finished transfering file $file"
        fi
    done
