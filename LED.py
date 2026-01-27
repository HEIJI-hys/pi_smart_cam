import time
import spidev
import numpy as np
import alsaaudio
from gpiozero import LED as GPIO_LED

# --- Hardware Setup ---
power = GPIO_LED(5)
power.on()
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000

# --- Audio Setup ---
card_idx = -1
for i, name in enumerate(alsaaudio.cards()):
    if "respeaker" in name.lower():
        card_idx = i
        break
if card_idx != -1:
    device = f'hw:{card_idx}'
else:
    print("ReSpeaker not found!")

mic = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, 
                    channels=4, rate=16000, 
                    format=alsaaudio.PCM_FORMAT_S16_LE, 
                    periodsize=160, device)

def set_ring(r, g, b, brightness=2):
    data = [0x00] * 4
    for _ in range(12):
        data.extend([0xE0 | brightness, b, g, r])
    data.extend([0xFF] * 4)
    spi.xfer2(data)

print("Starting Color-Level Visualizer... (Ctrl+C to stop)")

try:
    while True:
        length, data = mic.read()
        
        if length > 0:
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_data**2))
            
            # --- COLOR LOGIC ---
            # Quiet (Volume < 500): Subtle Green
            if volume < 500:
                set_ring(0, 50, 0) 
            
            # Normal Speaking (500 - 2000): Yellow/Orange
            elif 500 <= volume < 2000:
                set_ring(255, 150, 0)
                
            # Loud (Volume > 2000): Bright Red
            else:
                set_ring(255, 0, 0)
                
        time.sleep(0.01) # Small sleep to prevent CPU spiking

except KeyboardInterrupt:
    print("\nCleaning up...")
finally:
    set_ring(0, 0, 0)
    spi.close()
    power.off()