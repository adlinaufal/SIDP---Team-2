def GetGPSData():
    latitude = None
    longitude = None

    serial_port = "/dev/ttyS0"
    serial_fd = open_serial_port(serial_port)
    if serial_fd:
        try:
            gps_data = read_gps_data(serial_fd)
            print("Raw GPS data:", gps_data)  # Print raw data for debugging
            if gps_data:
                lines = gps_data.splitlines()
                for line in lines:
                    msg_str = line.strip()
                    msg_list = msg_str.split(",")

                    if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
                        if msg_list[GPGSA_dict['mode2']] == "1":
                            print("!!!!!!!Failed to obtain GPS coordinates.!!!!!!!\n")
                            os.close(serial_fd)
                            return None, None
                        else:
                            print("***GPS coordinates successfully retrieved.***\n")

                    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
                        for key, value in GPGGA_dict.items():
                            if key == "latitude":
                                latitude = msg_list[GPGGA_dict[key]]
                            elif key == "longitude":
                                longitude = msg_list[GPGGA_dict[key]]

                os.close(serial_fd)
                if latitude and longitude:
                    return latitude, longitude
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
