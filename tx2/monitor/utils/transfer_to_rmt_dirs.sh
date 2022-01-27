#!/bin/bash

lftp -e "put -O '$1/' '$2' ; bye" ftp.itc.nl
