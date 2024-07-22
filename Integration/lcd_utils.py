import os
import sys
import time
from PIL import Image

sys.path.append("..")

import LCD2inch4_lib

WHITE = 0xFF
BLACK = 0x00

def lcd_display(userId):
    SPI_DEVICE = "/dev/spidev1.0"

    disp = LCD2inch4_lib.LCD_2inch4(11, 40, SPI_DEVICE)
    disp.lcd_init_2inch4()

    # Retrieve the image
    image_path = os.path.join("images", f"{userId}.jpg")

    # Display the obtained image
    image = Image.open(image_path)
    image = image.resize((320, 240))
    disp.lcd_ShowImage(image, 0, 0)
    time.sleep(2)

    # Clear the display
    disp.lcd_init_2inch4()
    disp.lcd_clear(BLACK)

