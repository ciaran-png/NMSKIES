from flask import Flask, request, jsonify, render_template
import threading
from run_it_up2 import run_apiinteraction, update_image_label, automated_observation_cycle, run_automated2, schedule_automation_function

from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_tle_updater', methods=['POST'])
def run_tle_updater():
    # Asynchronously run the TLE updater script
    thread = threading.Thread(target=run_apiinteraction)
    thread.start()
    return jsonify({"status": "TLE Updater initiated"})

@app.route('/update_image', methods=['GET'])
def update_image():
    # Asynchronously update the image label
    thread = threading.Thread(target=update_image_label)
    thread.start()
    return jsonify({"status": "Image update initiated"})

@app.route('/start_observation_cycle', methods=['POST'])
def start_observation_cycle():
    # Asynchronously start the automated observation cycle
    thread = threading.Thread(target=automated_observation_cycle)
    thread.start()
    return jsonify({"status": "Observation cycle started"})

@app.route('/run_automated2', methods=['POST'])
def run_automated2_route():
    # Asynchronously run the automated2 script
    thread = threading.Thread(target=run_automated2)
    thread.start()
    return jsonify({"status": "Automated2 script initiated"})

@app.route('/schedule_automation', methods=['POST'])
def schedule_automation():
    # Asynchronously schedule the automation function
    thread = threading.Thread(target=schedule_automation_function)
    thread.start()
    return jsonify({"status": "Automation scheduling initiated"})

if __name__ == '__main__':
    socketio.run(app)