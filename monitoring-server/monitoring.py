from flask import Flask, render_template, request, jsonify, Response, json
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import redis
import json
import subprocess
import Adafruit_DHT as dht

garage_current_state = {}

app = Flask(__name__)
red = redis.StrictRedis()
red.from_url("redis://127.0.0.1:6379/0")

#Set thermometer data pin
DHT = 17

def write_txt(data, filename='garage_logs.txt'):
	with open(filename,'a') as f:
		f.write(f"{data['door_status']}\t date:{data['date']}\t time:{data['time']}\n")

def event_stream():
	pubsub = red.pubsub()
	pubsub.subscribe('door_activity')
	# TODO: handle client disconnection.
	try:
		for message in pubsub.listen():
			if message['type']=='message':
				yield('data: %s\n\n' % message['data'].decode('utf-8'))
	finally:
		i = 0

#===========================================================================================
#Analyze use cases to see if you need both endpoints or just one /history
@app.route('/history', methods=['GET'])
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


@app.route('/climate', methods=['GET'])
def climate():
	try:
		humidity, temperature = dht.read_retry(dht.DHT22, DHT)

		current_climate = {
			"temperature": temperature,
			"humidity": humidity
		}

		response = Response(response=json.dumps(current_climate), status=200, mimetype='application/json')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response
	except Exception as e:
		print(f'/climate. Unable to process. Reason: {e}')

		response = Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response

@app.route('/lastactivity', methods=['GET'])
def get_last_activity():
	#Need to wrap this in try/catch

	try:
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
#===========================================================================================

@app.route('/openalert', methods=['POST'])
def send_alert():
	try:
		minutes_opened = request.args.get('minutes')
		if not minutes_opened:
			raise AssertionError("No 'minutes' param sent")
		print(f"WARNING: Garage door has been opened for {minutes_opened} minutes")

		garage_still_open = {}

		garage_still_open['door_status'] = 'still_open'
		garage_still_open['minutes_opened'] = minutes_opened

		red.publish('door_activity', json.dumps(garage_still_open))

		#########################################################
		#Send Amazon SNS text message to phone for notifications
		#########################################################

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

		#POST sensor change status date/time to AWS to send SMS notification
		#TODO Wrap this in try catch?

		# with open("/home/pi/auth/api_key.json") as json_file:
		# 	data = json.load(json_file)
		# 	url = data["smart-garage-notification-url"]
		# 	api_key = data["x-api-key"]
			
		# 	aws_response = requests.post(url=url,
        #                         		params={'door_status': door_status},
		# 								headers={'x-api-key': api_key}
		# 							)

		#====================================================================================
		# Garage usage log entry to be appended
		log_entry = {"door_status": request.args.get('door_status'),
						"date": request.args.get('date'),
						"time": request.args.get('time')
					}

		#Write logs into json file
		write_txt(log_entry)
		#====================================================================================

		red.publish('door_activity', json.dumps(garage_current_state))

		return Response('OK', status=200, mimetype='text/html')

	except AssertionError as a:
		return Response(f'Unable to process. Reason: {a}', status=400, mimetype='text/html')
	except Exception as e:
		print(e)
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

@app.route('/stream')
def stream():
    response = Response(event_stream(),
                          mimetype="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5001, ssl_context=('/home/pi/auth/cert.pem', '/home/pi/auth/key.pem'))
