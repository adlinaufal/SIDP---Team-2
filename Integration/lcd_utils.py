import os
import time
from PIL import Image
import LCD2inch4_lib

WHITE = 0xFF
BLACK = 0x00

# Create a global instance for the LCD display
disp = None

def initialize_lcd():
    global disp
    if disp is None:
        SPI_DEVICE = "/dev/spidev1.0"
        disp = LCD2inch4_lib.LCD_2inch4(11, 40, SPI_DEVICE)
        disp.lcd_init_2inch4()
    return disp

def lcd_display(userId, current_directory):
    global disp
    if disp is None:
        initialize_lcd()

    try: 
        # Retrieve the image
        image_path = os.path.join("images", f"{userId}.jpg")

        # Display the obtained image
        image = Image.open(image_path)
        image = image.resize((320, 240))
        disp.lcd_ShowImage(image, 0, 0)
        time.sleep(2)

        # Reinitialize the display to ensure the whole screen is cleared
        blackImage = Image.open(os.join.path(current_directory, "image.png"))
        blackImage = blackImage.resize((320, 240))
        disp.lcd_ShowImage(blackImage, 0, 0)

    except:
        pass
