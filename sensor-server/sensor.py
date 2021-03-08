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
	print(time_opened)
	try:
		##################################################################################################################
		#POST open status date/time to monitoring server
		sensorchange = requests.get('http://localhost:5001/sensorchange',
									params={'door_status': "opened",
											'date': time_opened.strftime("%x"),
											'time': time_opened.strftime("%X")})
		##################################################################################################################
	except Exception as e:
		###########################################################
		# TODO: LOG ERROR AND COME UP WITH WAY TO ALERT OF FAILURE
		###########################################################
		print(f"CANNOT SEND DOOR OPENED STATUS TO MONITORING SERVER. {e}")
	while(1):
		time_now = datetime.now()
		if((int((time_now-time_opened).total_seconds()) % 600) == 0 and
			(int((time_now-time_opened).total_seconds()) != 0)):
			try:
				##################################################################################################################
				#Send GET to monitoring server /openalert endpoint if door is open for 10 minutes
				openalert = requests.get('http://localhost:5001/openalert',
										 params={'minutes': int((time_now-time_opened).total_seconds() / 60)})
				##################################################################################################################
			except Exception as e:
				###########################################################
				# TODO: LOG ERROR AND COME UP WITH WAY TO ALERT OF FAILURE
				###########################################################
				print(f"CANNOT SEND ALERT TO MONITORING SERVER. {e}")
			print(f"WARNING: Garage has been open for {int((time_now-time_opened).total_seconds() / 60)} minutes")
			sleep(1)
		if(GPIO.input(16) == GPIO.HIGH):
			print(f"Door was opened for {(time_now-time_opened).total_seconds()}")
			return


def door_closed():
	print("Door is closed")
	time_closed = datetime.now()
	print(time_closed)
	try:
		#########################################################
		#POST close status date/time to monitoring server
		sensorchange = requests.get('http://localhost:5001/sensorchange',
								params={'door_status': "closed",
										'date': time_closed.strftime("%x"),
										'time': time_closed.strftime("%X")})
		#########################################################
	except Exception as e:
		###########################################################
		# TODO: LOG ERROR AND COME UP WITH WAY TO ALERT OF FAILURE
		###########################################################
		print(f"CANNOT SEND DOOR CLOSED STATUS TO MONITORING SERVER. {e}")
	while(1):
		if(GPIO.input(16) == GPIO.LOW):
			print(f"Door was opened for {(datetime.now()-time_closed).total_seconds()}")
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
	except Exception as e:
		print(f"Sensor service failed: {e}")




if __name__ == "__main__":
    main()