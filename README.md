# smart-garage-backend

This is the source code for the backend server of the garage. It includes:

* garage-control-server: Controls the opening and closing the garage door
* monitoring-server: This includes:
    - /sensorchange - Detects the open and close of the garage door and writes it to a log file
    - /openalert - Sends an AWS SNS notification if the garage has been open for a long period of time
    - /lastactivity - Gets the last activity of the garage door use when the smart-garage frontend is accessed. The last activity is holds the current status of the garage door.
    - /history - Gets usage log history of the garage door
    - /stream - Redis stream to send push notifications of when garage door is opened, closed, or has been opened for a long period
    - /climate - Gets the current temperature and humidity of the garage
* sensor-server: Door sensor loop which monitors the open/close status of the garage door

Install the prerequisites:

`python3 -m pip install -r requirements.txt`

Run server:

`./autostart.sh`

**Please note:** You will need to install tmux and tmuxinator

To startup automatically on boot add this to /etc/rc.local

`runuser -l pi /home/pi/smart-garage-backend/autostart.sh &`

