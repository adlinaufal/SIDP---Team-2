import time
import VisionFive.spi as spi
import VisionFive.gpio as gpio
import numpy as np
from PIL import Image


class LCD_2inch4:
    width = 240
    height = 320

    def __init__(self, rst_pin, dc_pin, dev):
        gpio.setmode(gpio.BOARD)
        
        self.rstpin = rst_pin
        self.dcpin = dc_pin
        self.spidev = dev
        spi.getdev(self.spidev)

        """Reset the maximum clock frequency of communication"""
        """The display speed of the picture is positively correlated with the clock frequency"""
        # spi.setmode(500000, 0, 8)
        spi.setmode(40000000, 0, 8)
        gpio.setup(self.rstpin, gpio.OUT)
        gpio.setup(self.dcpin, gpio.OUT)

    def __del__(self):
        spi.freedev()

    """add a short delay for each change of electrical level"""

    def lcd_reset(self):
        gpio.output(self.rstpin, gpio.HIGH)
        time.sleep(0.01)
        gpio.output(self.rstpin, gpio.LOW)
        time.sleep(0.01)
        gpio.output(self.rstpin, gpio.HIGH)
        time.sleep(0.01)

    def lcd_spisend(self, data):
        spi.transfer(data)

    def lcd_sendcmd(self, cmd):
        gpio.output(self.dcpin, gpio.LOW)
        spi.transfer(cmd)

    def lcd_senddata(self, data):
        gpio.output(self.dcpin, gpio.HIGH)
        spi.transfer(data)

    """write multiple bytes"""

    def lcd_sendnbytes(self, data):
        gpio.output(self.dcpin, gpio.HIGH)
        spi.write(data)

    """common registers' initialization of 2.4inch LCD module"""

    def lcd_init_2inch4(self):
        self.lcd_reset()

        self.lcd_sendcmd(0x11)  # sleep out

        self.lcd_sendcmd(0xCF)  # Ppower Control B
        self.lcd_senddata(0x00)
        self.lcd_senddata(0xC1)
        self.lcd_senddata(0x30)

        self.lcd_sendcmd(0xED)  # Power on sequence control
        self.lcd_senddata(0x64)
        self.lcd_senddata(0x03)
        self.lcd_senddata(0x12)
        self.lcd_senddata(0x81)

        self.lcd_sendcmd(0xE8)  # Driver Timing Control A
        self.lcd_senddata(0x85)
        self.lcd_senddata(0x00)
        self.lcd_senddata(0x79)

        self.lcd_sendcmd(0xCB)  # Power Control A
        self.lcd_senddata(0x39)
        self.lcd_senddata(0x2C)
        self.lcd_senddata(0x00)
        self.lcd_senddata(0x34)
        self.lcd_senddata(0x02)

        self.lcd_sendcmd(0xF7)  # Pump ratio control
        self.lcd_senddata(0x20)

        self.lcd_sendcmd(0xEA)  # Driver Timing Control B
        self.lcd_senddata(0x00)
        self.lcd_senddata(0x00)

        self.lcd_sendcmd(0xC0)  # Power Control 1
        self.lcd_senddata(0x1D)  # VRH[5:0]

        self.lcd_sendcmd(0xC1)  # Power Control 2
        self.lcd_senddata(0x12)  # SAP[2:0],BT[3:0]

        self.lcd_sendcmd(0xC5)  # VCOM Control 1
        self.lcd_senddata(0x33)
        self.lcd_senddata(0x3F)

        self.lcd_sendcmd(0xC7)  # VCOM Control 2
        self.lcd_senddata(0x92)

        self.lcd_sendcmd(0x3A)  # COLMOD:Pixel Format Set
        self.lcd_senddata(0x55)

        self.lcd_sendcmd(0x36)  # Memory Access Control
        self.lcd_senddata(0x08)

        self.lcd_sendcmd(0xB1)  # Frame Rate Control(In Normal Mode/Full Colors)
        self.lcd_senddata(0x00)
        self.lcd_senddata(0x12)

        self.lcd_sendcmd(0xB6)  # Display Function Control
        self.lcd_senddata(0x0A)
        self.lcd_senddata(0xA2)

        self.lcd_sendcmd(0x44)  # Set_Tear_Scanline
        self.lcd_senddata(0x02)

        self.lcd_sendcmd(0xF2)  # 3Gamma Function Disable
        self.lcd_senddata(0x00)

        self.lcd_sendcmd(0x26)  # Gamma curve selected
        self.lcd_senddata(0x01)

        self.lcd_sendcmd(0xE0)  # Set Gamma
        self.lcd_senddata(0x0F)
        self.lcd_senddata(0x22)
        self.lcd_senddata(0x1C)
        self.lcd_senddata(0x1B)
        self.lcd_senddata(0x08)
        self.lcd_senddata(0x0F)
        self.lcd_senddata(0x48)
        self.lcd_senddata(0xB8)
        self.lcd_senddata(0x34)
        self.lcd_senddata(0x05)
        self.lcd_senddata(0x0C)
        self.lcd_senddata(0x09)
        self.lcd_senddata(0x0F)
        self.lcd_senddata(0x07)
        self.lcd_senddata(0x00)

        self.lcd_sendcmd(0xE1)  # Set Gamma
        self.lcd_senddata(0x00)
        self.lcd_senddata(0x23)
        self.lcd_senddata(0x24)
        self.lcd_senddata(0x07)
        self.lcd_senddata(0x10)
        self.lcd_senddata(0x07)
        self.lcd_senddata(0x38)
        self.lcd_senddata(0x47)
        self.lcd_senddata(0x4B)
        self.lcd_senddata(0x0A)
        self.lcd_senddata(0x13)
        self.lcd_senddata(0x06)
        self.lcd_senddata(0x30)
        self.lcd_senddata(0x38)
        self.lcd_senddata(0x0F)
        self.lcd_sendcmd(0x29)  # Display on

    def lcd_setPos(self, Xstart, Ystart, Xend, Yend):
        self.lcd_sendcmd(0x2A)
        self.lcd_senddata(Xstart >> 8)
        self.lcd_senddata(Xstart & 0xFF)
        self.lcd_senddata((Xend - 1) >> 8)
        self.lcd_senddata((Xend - 1) & 0xFF)
        self.lcd_sendcmd(0x2B)
        self.lcd_senddata(Ystart >> 8)
        self.lcd_senddata(Ystart & 0xFF)
        self.lcd_senddata((Yend - 1) >> 8)
        self.lcd_senddata((Yend - 1) & 0xFF)
        self.lcd_sendcmd(0x2C)

    def lcd_clear(self, color):
        """Clear contents of image buffer"""

        _buffer = [color] * (self.width * self.height * 2)

        self.lcd_setPos(0, 0, self.width * 2, self.height)
        gpio.output(self.dcpin, gpio.HIGH)

        """modify the original single byte write to multi byte write"""
        # for i in range(0,len(_buffer)):
        #    self.lcd_spisend(_buffer[i])
        self.lcd_sendnbytes(_buffer)

    def lcd_ShowImage(self, Image, Xstart, Ystart):
        """Set buffer to value of Python Imaging Library image."""
        """Write display buffer to physical display"""
        imwidth, imheight = Image.size

        if imwidth == self.height and imheight == self.width:
            img = np.asarray(Image)
            pix = np.zeros((self.width, self.height, 2), dtype=np.uint8)
            # RGB888 >> RGB565
            pix[..., [0]] = np.add(
                np.bitwise_and(img[..., [0]], 0xF8), np.right_shift(img[..., [1]], 5)
            )
            pix[..., [1]] = np.add(
                np.bitwise_and(np.left_shift(img[..., [1]], 3), 0xE0),
                np.right_shift(img[..., [2]], 3),
            )
            pix = pix.flatten().tolist()

            self.lcd_sendcmd(
                0x36
            )  # define read/write scanning direction of frame memory
            self.lcd_senddata(0x78)
            self.lcd_setPos(0, 0, self.height, self.width)

            gpio.output(self.dcpin, gpio.HIGH)

            """modify the original single byte write to multi byte write"""
            # for i in range(0,len(pix),1):
            #   self.lcd_spisend(pix[i])
            self.lcd_sendnbytes(pix)
        else:
            img = np.asarray(Image)
            pix = np.zeros((imheight, imwidth, 2), dtype=np.uint8)

            pix[..., [0]] = np.add(
                np.bitwise_and(img[..., [0]], 0xF8), np.right_shift(img[..., [1]], 5)
            )
            pix[..., [1]] = np.add(
                np.bitwise_and(np.left_shift(img[..., [1]], 3), 0xE0),
                np.right_shift(img[..., [2]], 3),
            )

            pix = pix.flatten().tolist()

            self.lcd_sendcmd(0x36)
            self.lcd_senddata(0x08)
            self.lcd_setPos(0, 0, self.width, self.height)

            gpio.output(self.dcpin, gpio.HIGH)

            """modify the original single byte write to multi byte write"""
            # for i in range(0,len(pix)):
            #    self.lcd_spisend(pix[i])
            self.lcd_sendnbytes(pix)
