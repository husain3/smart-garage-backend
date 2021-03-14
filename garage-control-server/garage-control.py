from flask import Flask, render_template, request, jsonify, Response
import json
import time
import RPi.GPIO as GPIO
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash

from flask_basicauth import BasicAuth


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)

app = Flask(__name__)
cors = CORS(app)

f = open('config.json')
data = json.load(f)
user = data["user"]
f.close()

app.config['BASIC_AUTH_USERNAME'] = user['username']
app.config['BASIC_AUTH_PASSWORD'] = user['password']

basic_auth = BasicAuth(app)

@app.route('/openclose', methods=['POST'])
@cross_origin()
@basic_auth.required
def Garage():
	try:
		GPIO.output(7, GPIO.LOW)
		time.sleep(1)
		GPIO.output(7, GPIO.HIGH)
		time.sleep(2)

		response = Response('OK', status=200, mimetype='text/html')
		# response.headers["Access-Control-Allow-Origin"] = "*"

		return response
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)