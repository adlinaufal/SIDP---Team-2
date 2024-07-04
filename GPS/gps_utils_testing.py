import sys
import serial
import time


GPGSA_dict = {
"msg_id": 	0,
"mode1": 	1,
"mode2": 	2,
"ch1":          3,
"ch2":          4,
"ch3":          5,
"ch4":          6,
"ch5":          7,
"ch6":          8,
"ch7":          9,
"ch8":          10,
"ch9":          11,
"ch10":         12,
"ch11":         13,
"ch12":         14,
}

GPGGA_dict = {
"msg_id": 		0,
"utc": 		        1,
"latitude":             2,
"NorS":                 3,
"longitude":            4,
"EorW":                 5,
"pos_indi":             6,
"total_Satellite":      7,
}

uart_port = "/dev/ttyS0"

def IsValidGpsinfo(gps):
    data = gps.readline()
    #Convert the data to string. 
    msg_str = str(data, encoding="utf-8")
    #Split string with ",".
    #GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
    msg_list = msg_str.split(",")
    
    #Parse the GPGSA message.
    if (msg_list[GPGSA_dict['msg_id']] == "$GPGSA"):
            print()
            #Check if the positioning is valid.
            if msg_list[GPGSA_dict['mode2']] == "1":
                print("!!!!!!Positioning is invalid!!!!!!")
            else:
                print("*****GPS coordinates successfully retrieved*****".format(msg_list[GPGSA_dict['mode2']]))
                
    #Parse the GPGGA message. 
    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
        print()
        for key, value in GPGGA_dict.items():
            #Parse the utc information.
            #if key == "utc":
            #    utc_str =  msg_list[GPGGA_dict[key]]
            #    if not utc_str == '':
            #        h = int(utc_str[0:2])
            #        m = int(utc_str[2:4])
            #        s = float(utc_str[4:])
            #        print(" utc time: {}:{}:{}".format(h,m,s))
            #        print(" {} time: {} (format: hhmmss.sss)".format(key, msg_list[GPGGA_dict[key]]))
            #Parse the latitude information.
            if key == "latitude":
                latitude = msg_list[GPGGA_dict[key]]
                if not latitude == '':
                    Len = len(latitude.split(".")[0])
                    d = int(latitude[0:Len-2])
                    m = float(latitude[Len-2:])
                    #print(" latitude: {} degree {} minute".format(d, m))
                    print(" {}: {}".format(key, latitude))
            #Parse the longitude information.
            elif key == "longitude":
                longitude = msg_list[GPGGA_dict[key]]
                if not longitude == '':
                    Len = len(longitude.split(".")[0])
                    d = int(longitude[0:Len-2])
                    m = float(longitude[Len-2:])
                    #print(" longitude: {} degree {} minute".format(d, m))
                    print(" {}: {}".format(key, longitude))
            else:
                print(" {}: {}".format(key, msg_list[GPGGA_dict[key]]))

def main():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        IsValidGpsinfo(gps)
        time.sleep(1)
    
    gps.close()
                
if __name__ == "__main__":
    sys.exit(main())