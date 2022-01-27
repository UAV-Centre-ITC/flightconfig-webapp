#!/bin/bash

TIMEFORMAT=%R

MONITORDIR=$1
echo "MONITOR_PIPE - DIR TO MONITOR IS" $MONITORDIR

inotifywait -m -r "${MONITORDIR}" -e create|
    while read dir action file; do
        if [ $action == "CREATE" ]; then
            time echo "$MONITORDIR/$file"
        fi
    done
