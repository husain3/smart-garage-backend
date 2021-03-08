import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep
import requests

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Do Anass style commenting
def door_open():
	print("Door is open")
	time_opened = datetime.now()
	#########################################################
	#POST open status date/time to monitoring server
	#########################################################
	while(1):
		if((int((datetime.now()-time_opened).total_seconds()) % 600) == 0 and (int((datetime.now()-time_opened).total_seconds()) != 0)):
			try:
				#########################################################
				#Send POST to monitoring server /openalert endpoint if door is open for 10 minutes
				r = requests.get('http://localhost:5001/openalert', params={'minutes': int((datetime.now()-time_opened).total_seconds() / 60)})
				#########################################################
			except Exception as e:
				###########################################################
				# TODO: LOG ERROR AND COME UP WITH WAY TO ALERT OF FAILURE
				###########################################################
				print(f"CANNOT SEND ALERT TO MONITORING SERVER. {e}")
			print(f"WARNING: Garage has been open for {int((datetime.now()-time_opened).total_seconds() / 60)} minutes")
			sleep(1)
		if(GPIO.input(16) == GPIO.HIGH):
			time_closed = datetime.now()
			print(f"Door was opened for {(time_closed-time_opened).total_seconds()}")
			return


def door_closed():
	print("Door is closed")
	while(1):
		#########################################################
		#POST close status date/time to monitoring server]
		#########################################################
		if(GPIO.input(16) == GPIO.LOW):
			return

def main():
	try:
		while(1):
			if(GPIO.input(16) == GPIO.LOW):
				door_open()
			else:
				door_closed()
	except KeyboardInterrupt:
		print("Ctrl-C Recieved. Closing sensor.py")




if __name__ == "__main__":
    main()