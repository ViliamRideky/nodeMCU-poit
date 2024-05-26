import serial
import time
import json  

# Nastavenie sériovej komunikácie
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

try:
    while True:
        # Čítanie údajov zo sériovej komunikácie
        line = ser.readline().decode('utf-8').strip()
        
        if line:  
            try:
                data = json.loads(line)  
                print("Teplota:", data.get('temperature', 'N/A'), "°C")
                print("Vlhkosť:", data.get('humidity', 'N/A'), "%")
            except json.JSONDecodeError:
                print("Chyba pri dekódovaní JSON: ", line)
        
        time.sleep(1)

except KeyboardInterrupt:
    ser.close()
