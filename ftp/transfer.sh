#!/bin/bash

inotifywait -m /home/jetsontx2/Data/images -e create -e moved_to |
    while read dir action file; do
        echo "The file '$file' appeared in directory '$dir'via '$action'"
        kill -2 $$
    done
    
lftp -e "mkdir /pub/DeltaQuad/'$file'; mirror -R /home/jetsontx2/Data/images/'$file' /pub/DeltaQuad/'$file'; bye" ftp.itc.nl

