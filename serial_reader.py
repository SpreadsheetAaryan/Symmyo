import serial
import csv
import time
import os
import random # Used for simulation if needed

# --- Configuration ---
# NOTE: Replace with your actual settings
SERIAL_PORT = '/dev/cu.usbmodem14101'  # Example port on macOS/Linux. Check your Arduino/Delsys port!
BAUD_RATE = 115200  # Match this to your EMG board's output rate (e.g., 115200 or 9600)
CSV_FILENAME = 'real_time_log.csv'
CHANNELS = ['Time_ms', 'iliacus_left', 'iliacus_right', 'psoas_left', 'psoas_right']
# ---------------------

def initialize_serial(port, baudrate):
    """Initializes and returns the serial connection."""
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        time.sleep(2)  # Give time for the port to initialize
        ser.flushInput()
        print(f"Successfully connected to {port} at {baudrate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        print("Please check the port name and ensure the device is plugged in.")
        return None

def initialize_csv(filename, header):
    """Initializes the CSV file with headers if it doesn't exist."""
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists or os.path.getsize(filename) == 0:
            writer.writerow(header)
            print(f"Initialized CSV file: {filename}")
        return writer, f

def start_data_logging():
    """Reads serial data continuously, logs to CSV, and prints."""
    ser = initialize_serial(SERIAL_PORT, BAUD_RATE)
    if ser is None:
        return

    writer, f = initialize_csv(CSV_FILENAME, CHANNELS)
    
    start_time = time.time()
    last_log_time = start_time

    try:
        while True:
            # 1. Read Raw Serial Data
            # Assumes your board outputs a comma-separated string like "42.5,1.1,-0.8,0.5"
            raw_line = ser.readline().decode('utf-8').strip()
            
            if raw_line:
                # 2. Parse and Time-Stamp
                current_time_ms = int((time.time() - start_time) * 1000)
                
                # Split the sensor readings (must handle potential garbage/malformed data)
                readings = raw_line.split(',')
                
                # Check if we received the expected number of sensor values (4 in your case)
                if len(readings) == 4:
                    try:
                        # Convert to numbers (float is safest)
                        sensor_values = [float(val.strip()) for val in readings]
                        
                        # Data Row: [Time_ms, Sensor1, Sensor2, Sensor3, Sensor4]
                        data_row = [current_time_ms] + sensor_values
                        
                        # 3. Dynamic Write to CSV
                        writer.writerow(data_row)
                        f.flush() # Forces the data to be written immediately to disk

                        # 4. Optional: Print/Process (for display or sending to Flask/SocketIO)
                        # We would integrate the processing pipeline here
                        # print(f"Logged: {data_row}") 
                        
                    except ValueError:
                        # Handle cases where the string couldn't be converted to a float
                        print(f"Skipping malformed data: {raw_line}")
                
            # Simulate a small delay to avoid consuming 100% CPU if data stream is slow
            # If your board streams at a high rate (1000 Hz), remove this delay.
            # time.sleep(0.001) 
            
    except KeyboardInterrupt:
        print("\nData logging stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed.")
        if 'f' in locals() and not f.closed:
            f.close()
            print(f"CSV file '{CSV_FILENAME}' closed.")


if __name__ == '__main__':
    # You would typically run this file in a separate terminal on your host machine (macOS)
    start_data_logging()