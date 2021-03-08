import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Do Anass style commenting
def door_open():
	print("Door is open")
	while(1):
		#POST open status date/time to monitoring server
		if(GPIO.input(16) == GPIO.HIGH):
			return


def door_closed():
	print("Door is closed")
	while(1):
		#POST close status date/time to monitoring server
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