#!/bin/bash

cd /home/jetsontx2/Documents/django/tx2

./start_ngrok.sh & ./start_loc_serv.sh & ./start_celery.sh
