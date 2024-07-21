import os
import sys
import time
import logging
from PIL import Image, ImageDraw, ImageFont

sys.path.append("..")

import VisionFive.boardtype as board_t
import LCD2inch4_lib

WHITE = 0xFF
BLACK = 0x00

def lcd_display(imgS):
    vf_t = board_t.boardtype()
    SPI_DEVICE = "/dev/spidev1.0"

    disp = LCD2inch4_lib.LCD_2inch4(11, 40, SPI_DEVICE)
    disp.lcd_init_2inch4()

    # Display an image
#    image = Image.open("./adli-naufal_721202462550.jpg")
    image = Image.open(imgS)
    image = image.resize((320, 240))
    disp.lcd_ShowImage(image, 0, 0)
    time.sleep(5)

    # Clear the display
    disp.lcd_init_2inch4()
    disp.lcd_clear(WHITE)

    # Create an image with text
    text_image = Image.new('RGB', (320, 240), color=(255, 255, 255))
    draw = ImageDraw.Draw(text_image)

    # Define the font and size
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()

    # Define the text and position
    text = "Hello, Nigger!"
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (320 - text_width) // 2
    text_y = (240 - text_height) // 2

    # Draw the text on the image
    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0))

    # Display the text image on the LCD
    disp.lcd_ShowImage(text_image, 0, 0)
    time.sleep(5)
