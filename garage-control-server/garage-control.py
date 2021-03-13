from flask import Flask, render_template, request, jsonify, Response
import json
import time
import RPi.GPIO as GPIO
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    f = open('config.json')
    data = json.load(f)
    users = data["users"]
    f.close()

    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/openclose', methods=['POST'])
@auth.login_required
def Garage():
	try:
		GPIO.output(7, GPIO.LOW)
		time.sleep(1)
		GPIO.output(7, GPIO.HIGH)
		time.sleep(2)

		response = Response('OK', status=200, mimetype='text/html')
		response.headers["Access-Control-Allow-Origin"] = "*"

		return response
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)