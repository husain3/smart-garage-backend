#	================================================================================================
#	File	: monitoring.py
#	Purpose	: Monitors the garage door, logs usage, and measures indoor climate
#	================================================================================================

from flask import Flask, render_template, request, jsonify, Response, json
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import redis
import json
import subprocess
import Adafruit_DHT as dht
import threading
import atexit
from flask_cors import CORS, cross_origin

garage_current_state = {}

POOL_TIME = 60  # Seconds

# Climate dict to save temperature and humidity for fast access
current_climate = {}

# Lock to control access to variable
dataLock = threading.Lock()

# Thermometer thread handler
tempThread = threading.Thread()

#	================================================================================================
#	Function to initialize flask server and start climate thread routine
#	================================================================================================
def create_monitoring_server():
	app = Flask(__name__)

	#Set thermometer data pin
	DHT = 17

	#SIGTERM handler
	def interrupt():
		global tempThread
		tempThread.cancel()

	#Read thermometer and humidity sensor
	def getClimate():
		global current_climate
		global tempThread

		with dataLock:
			try:
				humidity = 0.0
				temperature = 0.0

				for i in range(3):
					humidity, temperature = dht.read_retry(dht.DHT22, DHT)
					print(f"{humidity}  {temperature}")

				temperature = round(temperature, 1)
				humidity = round(humidity, 1)

				current_climate["temperature"] = temperature
				current_climate["humidity"] = humidity

			except Exception as e:
				print(f"CANT GET CLIMATE: {e}")

		# Set the next thread to happen
		tempThread = threading.Timer(POOL_TIME, getClimate, ())
		tempThread.start()

	# Initialize climate reading routine
	def getClimateStart():
		# Initialize temperature thread
		global tempThread

		# Create your thread
		tempThread = threading.Timer(0, getClimate())
		tempThread.start()

	# Initiate
	getClimateStart()
	
	# SIGTERM handler registering
	atexit.register(interrupt)
	return app


app = create_monitoring_server()

#	================================================================================================
#	Writes the usage event to a plain text log file
#	================================================================================================
def write_txt(data, filename='garage_logs.txt'):
	with open(filename,'a') as f:
		f.write(f"{data['door_status'].upper()}\t{data['date']}\t{data['time']}\n")


#	================================================================================================
#	/history - Gets full log history of garage door
#	================================================================================================
@app.route('/history', methods=['GET'])
@cross_origin()
def get_log_history():
	#Need to wrap in try/catch
	try:
		content = ''
		content = content.join(str(n) for n in reversed(open("garage_logs.txt").readlines()))
		return render_template("garage_log.html", content=content)
	except Exception as e:
		response = Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response


#	================================================================================================
#	/climate - Gets current temperature and humidity of the garage area
#	================================================================================================
@app.route('/climate', methods=['GET'])
def climate():
	try:

		response = Response(response=json.dumps(current_climate), status=200, mimetype='application/json')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response
	except Exception as e:
		print(f'/climate. Unable to process. Reason: {e}')

		response = Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response

#	================================================================================================
#	/lastactivity - Gets the last activity of the garage door
#	================================================================================================
@app.route('/lastactivity', methods=['GET'])
def get_last_activity():
	try:
		#Fastest way to read the last line of a plain text file (last garage usage)
		line = subprocess.check_output(['tail', '-1', "garage_logs.txt"]).decode("utf-8")
		line = line.split()

		last_activity = {
			"door_status": line[0],
			"date": line[1],
			"time": line[2]
		}
		response = Response(response=json.dumps(last_activity), status=200, mimetype='application/json')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response
	except Exception as e:
		print(f'/lastactivity. Unable to process. Reason: {e}')

		response = Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response

#	================================================================================================
#	/openalert - Sends alert that the garage door as been open for a long period
#	================================================================================================
@app.route('/openalert', methods=['POST'])
def send_alert():
	try:
		minutes_opened = request.args.get('minutes')
		if not minutes_opened:
			raise AssertionError("No 'minutes' param sent")
		print(f"WARNING: Garage door has been opened for {minutes_opened} minutes")

		garage_still_open = {}

		garage_still_open['door_status'] = 'STILL_OPEN'
		garage_still_open['minutes_opened'] = minutes_opened

		#Send Amazon SNS text message to phone for notifications
		with open("/home/pi/auth/api_key.json") as json_file:
			data = json.load(json_file)
			url = data["smart-garage-notification-url"]
			api_key = data["x-api-key"]

		aws_response = requests.post(url=url,
									params={
										'door_status': garage_still_open['door_status'],
										'open_duration': garage_still_open['minutes_opened']
										},
									headers={'x-api-key': api_key}
									)

		return Response('OK', status=200, mimetype='text/html')

	except AssertionError as a:
		return Response(f'Unable to process. Reason: {a}', status=400, mimetype='text/html')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

#	================================================================================================
#	/sensorchange - Changes the open/close status of the garage door
#	================================================================================================
@app.route('/sensorchange', methods=['POST'])
def door_sensor_change():
	door_status = request.args.get('door_status')
	date = request.args.get('date')
	time = request.args.get('time')

	try:
		if not door_status or not date or not time:
			params_missing = "\n"
			if not door_status:
				params_missing+=str("door_status\n")
			if not date:
				params_missing+=str("date\n")
			if not time:
				params_missing+=str("time\n")

			#TODO: Return missing param arguments as json
			raise AssertionError(f"The following params are missing: {params_missing}")

		garage_current_state['door_status'] = door_status
		garage_current_state['date'] = date
		garage_current_state['time'] = time

		#POST sensor change status date/time to AWS to send SMS notification via SES
		with open("/home/pi/auth/api_key.json") as json_file:
			data = json.load(json_file)
			url = data["smart-garage-notification-url"]
			api_key = data["x-api-key"]

		aws_response = requests.post(url=url,
									params={
										'door_status': garage_current_state['door_status']
										},
									headers={'x-api-key': api_key}
									)

		# Garage usage log entry to be appended
		log_entry = {"door_status": request.args.get('door_status'),
						"date": request.args.get('date'),
						"time": request.args.get('time')
					}

		#Write logs into json file
		write_txt(log_entry)

		return Response('OK', status=200, mimetype='text/html')

	except AssertionError as a:
		return Response(f'Unable to process. Reason: {a}', status=400, mimetype='text/html')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
<<<<<<< HEAD
	#Make GET request to log server for last activity
	try:
		response = requests.get('http://localhost:5002/lastactivity')
		garage_current_state['door_status'] = response.json()['door_status']
		garage_current_state['date'] = response.json()['date']
		garage_current_state['time'] = response.json()['time']
	except Exception as e:
		print(f"Unable to get last activity {e}")

=======
>>>>>>> release/1.0.0
	app.run(debug=True, host='0.0.0.0', port=5001)
