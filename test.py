from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Pump on OUT1/OUT2
pump = Motor(forward=5, backward=6)
pump_enable = PWMOutputDevice(12)

print("Starting pump")

pump_enable.value = 1.0
pump.forward()

sleep(5)

pump.stop()
pump_enable.value = 0

print("Pump test complete")
