import serial
import time

# Nastavenie sériovej komunikácie
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

try:
    while True:
        # Čítanie údajov zo sériovej komunikácie
        line = ser.readline().decode('utf-8').strip()
        
        # Zobrazenie údajov v termináli
        print(line)
        
        # Čakanie 1 sekundu pred ďalším čítaním
        time.sleep(1)

except KeyboardInterrupt:
    # Pri stlačení Ctrl+C zastavíme program a zatvoríme sériovú komunikáciu
    ser.close()
