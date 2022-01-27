#!/bin/bash

RMTDIR=$1

lftp -e "mkdir -p '$RMTDIR'; bye" ftp.itc.nl
