#! /bin/bash

/usr/bin/python /usr/local/bin/pinspiroy.py --quiet &
echo $! > /var/run/pinspiroy.pid
