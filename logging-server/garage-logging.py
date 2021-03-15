from flask import Flask, render_template, request, jsonify, Response
import json
from os import path

app = Flask(__name__)

def write_json(data, filename='garage_logs.json'): 
	with open(filename,'w') as f: 
		json.dump(data, f, indent=4)

@app.route('/garageactivity', methods=['POST'])
def log_garage_activity():
	door_status = request.args.get('door_status')
	date = request.args.get('date')
	time = request.args.get('time')

	if not path.exists("garage_logs.json"):
		initLogJson = '''
{
	"garagedoor_usage_log": [

	]
}
'''

		f = open('garage_logs.json', 'w')
		f.write(initLogJson)
		f.close()

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

		with open('garage_logs.json') as json_file:
			data = json.load(json_file)
			log_entries = data["garagedoor_usage_log"]

			# Garage usage log entry to be appended
			log_entry = {"door_status": door_status,
						 "date": date,
						 "time": time
						}

			#Appending log entry given from params to json variable
			log_entries.append(log_entry)
			
			#Write logs into json file
			write_json(data)
		return Response('OK', status=200, mimetype='text/html')
	except AssertionError as a:
		print(f'/garageactivity. Unable to process. Reason: {e}')
		return Response(f'Unable to process. Reason: {a}', status=400, mimetype='text/html')
	except Exception as e:
		print(f'/garageactivity. Unable to process. Reason: {e}')
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

@app.route('/lastactivity', methods=['GET'])
def get_last_activity():
	try:
		if path.exists("garage_logs.json"):
			with open('garage_logs.json') as json_file:
				data = json.load(json_file)
				log_entries = data["garagedoor_usage_log"]
				last_entry = log_entries[-1:][0]
				response = Response(response=json.dumps(last_entry), status=200, mimetype='application/json')
				response.headers["Access-Control-Allow-Origin"] = "*"
				return response
		else:
			empty_entry = {
				"door_status": "N/A",
				"date": "N/A",
				"time": "N/A"
			}
			response = Response(response=json.dumps(empty_entry), status=200, mimetype='application/json')
			response.headers["Access-Control-Allow-Origin"] = "*"
			return response

	except Exception as e:
		print(f'/lastactivity. Unable to process. Reason: {e}')
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

@app.route('/history', methods=['GET'])
def get_log_history():
	try:
		with open('garage_logs.json') as json_file:
			data = json.load(json_file)
			log_entries = data["garagedoor_usage_log"]
			log_entries.reverse()
			# print(type(data))
			return Response(response=json.dumps(data), status=200, mimetype='application/json')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
		app.run(debug=True, host='0.0.0.0', port=5002)
