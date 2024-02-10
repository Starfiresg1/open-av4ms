#!/bin/bash

# Start the first process
/usr/bin/python2 /home/www/av4server.py &
  
# Start the second process
/usr/bin/python2 /home/www/webserver.py

sleep infinity
