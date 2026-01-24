import time
import spidev
from gpiozero import LED

# 1. Turn on the power to the LED ring
power = LED(5)
power.on()

# 2. Setup SPI for APA102 LEDs
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000

def set_leds(r, g, b, brightness=31):
    # APA102 Protocol: Start Frame (32 zeros)
    data = [0x00] * 4
    
    # LED Frames: [Brightness | 0xE0, B, G, R]
    # (Note: Brightness is 0-31)
    for _ in range(12):
        data.extend([0xE0 | brightness, b, g, r])
        
    # End Frame
    data.extend([0xFF] * 4)
    spi.xfer2(data)

try:
    print("Turning LEDs Blue...")
    set_leds(0, 0, 255) # Blue
    time.sleep(5)
    
    print("Turning LEDs off...")
    set_leds(0, 0, 0)
finally:
    power.off()
    spi.close()