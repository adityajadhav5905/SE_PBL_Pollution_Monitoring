import serial
import csv
from datetime import datetime

port = "COM5"  # Change this to your ESP32 COM port
baud = 115200
filename = f"sensor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

try:
    ser = serial.Serial(port, baud)
    print(f"Logging to {filename}...")

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        header_written = False

        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue

                # Remove timestamp prefix if present
                if "->" in line:
                    line = line.split("->", 1)[1].strip()

                data = line.split(",")

                if not header_written:
                    writer.writerow(["Sensor1", "Sensor2", "Sensor3"])  # Adjust as needed
                    header_written = True

                writer.writerow(data)
                print(data)
                file.flush()

            except UnicodeDecodeError:
                print("Decoding error – skipping line.")
except KeyboardInterrupt:
    print("\nLogging stopped by user.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
