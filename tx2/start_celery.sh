#!/bin/bash

# set environment
source /home/jetsontx2/Documents/django/tx2/djenv/bin/activate

cd ~/Documents/django/tx2

celery -A tx2.celery worker -l DEBUG -E
