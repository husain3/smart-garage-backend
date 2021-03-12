from flask import Flask, render_template, request, jsonify, Response, json
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import redis
import json

garage_current_state = {}

app = Flask(__name__)
red = redis.StrictRedis()
red.from_url("redis://127.0.0.1:6379/0")

def event_stream():
	pubsub = red.pubsub()
	pubsub.subscribe('door_activity')
	# TODO: handle client disconnection.
	for message in pubsub.listen():
		if message['type']=='message':
			yield('data: %s\n\n' % message['data'].decode('utf-8'))

@app.route('/openalert', methods=['POST'])
def send_alert():
	try:
		minutes_opened = request.args.get('minutes')
		if not minutes_opened:
			raise AssertionError("No 'minutes' param sent")
		print(f"WARNING: Garage door has been opened for {minutes_opened} minutes")
		#########################################################
		#Send Amazon SNS text message to phone for notifications
		#########################################################
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

		#POST sensor change status date/time to monitoring server
		#TODO Wrap this in try catch?
		sensorchange = requests.post('http://localhost:5002/garageactivity',
									params={'door_status': door_status,
											'date': date,
											'time': time})

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

@app.route('/current_state', methods=['GET'])
def door_current_state():
	try:
		return Response(json.dumps(garage_current_state), status=200, mimetype='application/json')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
	#Make GET request to log server for last activity
	response = requests.get('http://localhost:5002/lastactivity')
	garage_current_state['door_status'] = response.json()['door_status']
	garage_current_state['date'] = response.json()['date']
	garage_current_state['time'] = response.json()['time']

	app.run(debug=True, host='0.0.0.0', port=5001)
	app.config["REDIS_URL"] = "redis://127.0.0.1:6379/0"