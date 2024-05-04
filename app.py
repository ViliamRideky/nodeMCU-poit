from flask import Flask, render_template, jsonify
import serial
import time

app = Flask(__name__)

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=10)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/data")
def data():
    time.sleep(2)  # Pridanie oneskorenia pred každým čítaním
    buffer = ser.read(ser.inWaiting())
    if not buffer:
        return jsonify(temperature="No data", humidity="No data")
    lines = buffer.decode('utf-8').strip().split('\n')
    temp = None
    hum = None
    for line in lines:
        if 'Temperature' in line:
            temp = line.split(': ')[1].strip()
        elif 'Humidity' in line:
            hum = line.split(': ')[1].strip()
    
    # Kontrola, či sú hodnoty None a nevrátiť ich
    if temp is None or hum is None:
        return jsonify(temperature="No data", humidity="No data")
    return jsonify(temperature=temp, humidity=hum)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
