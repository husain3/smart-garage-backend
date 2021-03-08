from flask import Flask, render_template, request, jsonify, Response


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
		return 'OK'

	except AssertionError as a:
		return Response(f'Unable to process. Reason: {a}', status=400, mimetype='text/html')
	except Exception as e:
		return Response(f'Unable to process. Reason: {e}', status=500, mimetype='text/html')



if __name__ == "__main__":
		app.run(debug=True, host='0.0.0.0', port=5001)