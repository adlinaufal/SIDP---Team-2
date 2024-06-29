# gps_utils.py

import os
import fcntl
import termios  # Import termios for baud rate setting

# NMEA sentence indices for GPGSA and GPGGA
GPGSA_msg_id = 0
GPGSA_mode2 = 2
GPGGA_msg_id = 0
GPGGA_latitude = 2
GPGGA_longitude = 4

def open_serial_port(port):
    try:
        fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
        # Set baud rate (replace 9600 with your module's baud rate if different)
        serial_settings = termios.tcgetattr(fd)
        serial_settings[4] = termios.B9600  # Set baud rate to 9600 (adjust as needed)
        termios.tcsetattr(fd, termios.TCSANOW, serial_settings)
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        return fd
    except OSError as e:
        print(f"Error opening serial port {port}: {e}")
        return None

def read_gps_data(fd):
    try:
        data = os.read(fd, 256).decode('utf-8').strip()
        return data
    except OSError as e:
        print(f"Error reading from serial port: {e}")
        return None

def GetGPSData():
    latitude = None
    longitude = None

    serial_port = "/dev/ttyS6"
    serial_fd = open_serial_port(serial_port)
    
    if serial_fd:
        try:
            gps_data = read_gps_data(serial_fd)
            if gps_data:
                lines = gps_data.splitlines()
                for line in lines:
                    msg_list = line.split(",")
                    
                    if msg_list[0] == "$GPGGA" and len(msg_list) >= 10:
                        latitude = msg_list[GPGGA_latitude]
                        longitude = msg_list[GPGGA_longitude]
                        break  # Exit loop after finding GPGGA

                os.close(serial_fd)
                if latitude is not None and longitude is not None:
                    return latitude, longitude
                else:
                    print("Invalid GPS data format.")
                    return None, None
            else:
                print("Failed to read GPS data.")
                os.close(serial_fd)
                return None, None
        except Exception as e:
            print(f"Error processing GPS data: {e}")
            os.close(serial_fd)
            return None, None
    else:
        print(f"Failed to open serial port {serial_port}")
        return None, None
