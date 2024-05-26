from flask import Flask, render_template
from flask_socketio import SocketIO
import serial
import time
import threading
import json

app = Flask(__name__)
socketio = SocketIO(app)
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
system_active = False 

def read_from_port():
    global system_active
    while True:
        if system_active:  # Čítanie a odosielanie údajov len ak je systém aktívny
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    data = json.loads(line)
                    socketio.emit('newdata', data)
            except json.JSONDecodeError:
                print("Chyba pri dekódovaní JSON.")
            except UnicodeDecodeError:
                print("Dekódovanie zlyhalo.")
        time.sleep(1)

@socketio.on('initialize_system')
def initialize_system():
    global system_active
    print("Initializing system...")
    system_active = True  

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=read_from_port).start()
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
