from flask import Flask, render_template, request, jsonify, Response


garage_activity = {}

app = Flask(__name__)

@app.route('/openalert', methods=['GET'])
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

@app.route('/sensorchange', methods=['GET'])
def door_sensor_change():
	door_status = request.args.get('door_status')
	date = request.args.get('date')
	time = request.args.get('door_status')

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


		garage_activity = {
		    'door_status': door_status,
		    'date': date,
		    'time': time
		}


		#########################################################
		#Send POST in JSON form to the logging server, e.g.
		#{
		#	door_status: OPEN
		#	date: 05/29/2021
		#	time: 17:41:00
		#}
		#########################################################
		return Response('OK', status=200, mimetype='text/html')

	except AssertionError as a:
		return Response(f'Unable to process. Reason: {a}', status=400, mimetype='text/html')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
		app.run(debug=True, host='0.0.0.0', port=5001)