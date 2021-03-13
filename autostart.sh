#!/bin/bash

#Put this at before 'exit 0' in /etc/rc.local
#runuser -l pi /home/pi/smart-garage-backend/autostart.sh &

tmuxinator start -p /home/pi/smart-garage-backend/.tmuxinator.yml
