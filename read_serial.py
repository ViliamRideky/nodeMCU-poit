import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        print(line)
        time.sleep(1)

except KeyboardInterrupt:
    ser.close()