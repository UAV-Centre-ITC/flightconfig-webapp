#!/bin/bash

pubdir=/pub/DeltaQuad/test

lftp -e "mkdir -p '$pubdir'; bye" ftp.itc.nl
