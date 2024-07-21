import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
sys.path.append("..")
from lib import LCD2inch4_lib

# Define the color white for the LCD display
WHITE = 0xFF

def display_message(disp, message):
    # Create a blank white image
    width, height = 240, 320  # Adjust to match your LCD resolution
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # Initialize the drawing context
    draw = ImageDraw.Draw(image)
    
    # Define the font and size (Adjust path to your font if needed)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text size and position
    text_width, text_height = draw.textsize(message, font=font)
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    
    # Draw the text onto the image
    draw.text((text_x, text_y), message, font=font, fill=(0, 0, 0))
    
    # Display the image on the LCD
    disp.lcd_ShowImage(image, 0, 0)

def main():
    print('-----------lcd demo-------------')
    
    # The initialization settings of 2.4inch module.
    disp = LCD2inch4_lib.LCD_2inch4(44, 0, '/dev/spidev0.0')
    disp.lcd_init_2inch4()
    disp.lcd_clear(WHITE)
    
    # Display the message
    display_message(disp, "You are Good to Go")
    
    # Keep the message on the screen indefinitely
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
