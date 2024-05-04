from flask import Flask, render_template
import serial
import time

app = Flask(__name__)

# Nastavenie sériovej komunikácie
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

def read_serial_data():
    # Čítanie údajov zo sériovej komunikácie
    buffer = ser.read(ser.inWaiting())  # Prečíta všetky dostupné dáta
    if not buffer:
        return None, None  # Ak nie sú dostupné žiadne údaje, vráti None
    lines = buffer.decode('utf-8').strip().split('\n')
    temp = None
    hum = None
    for line in lines:
        if 'Temperature' in line:
            temp = line.split(': ')[1].strip()  # Zabezpečí odstránenie medzier
        elif 'Humidity' in line:
            hum = line.split(': ')[1].strip()
    return temp, hum

@app.route("/")
def index():
    temp, hum = read_serial_data()
    if temp is None or hum is None:
        temp = "Čakanie na údaje..."
        hum = "Čakanie na údaje..."
    return render_template('index.html', temperature=temp, humidity=hum)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
