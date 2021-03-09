from flask import Flask, render_template, request, jsonify, Response
import json
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)

app = Flask(__name__)

@app.route('/openclose', methods=['POST'])
def Garage():
	try:
		GPIO.output(7, GPIO.LOW)
		time.sleep(1)
		GPIO.output(7, GPIO.HIGH)
		time.sleep(2)
		return Response('OK', status=200, mimetype='text/html')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)