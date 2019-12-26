#! /bin/bash

if [ -f /var/run/pinspiroy.pid ]
then
        PID=$(< /var/run/pinspiroy.pid)
	kill -TERM $PID
	rm /var/run/pinspiroy.pid
fi
