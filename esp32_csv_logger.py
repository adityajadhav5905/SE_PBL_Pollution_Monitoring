import serial
import csv
from datetime import datetime

port = "COM5"  # Change this to your ESP32 COM port
baud = 115200
filename = f"sensor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

ser = serial.Serial(port, baud)
print(f"Logging to {filename}...")

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    header_written = False

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue
        if not header_written and line.startswith("Latitude"):
            writer.writerow(line.split(","))
            header_written = True
            continue
        elif header_written:
            writer.writerow(line.split(","))
            print(line)
