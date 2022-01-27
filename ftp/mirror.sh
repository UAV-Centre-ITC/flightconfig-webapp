#!/bin/bash

echo "newdir is $newdir"
lftp -e "mkdir /pub/DeltaQuad/'$newdir'; mirror -R /home/jetsontx2/Data/images/'$newdir' /pub/DeltaQuad/'$newdir'; bye" ftp.itc.nl
