from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Pump on OUT1/OUT2
pump = Motor(forward=5, backward=6)
pump_enable = PWMOutputDevice(12)

# TT Motor on OUT3/OUT4
tt_motor = Motor(forward=20, backward=21)
tt_enable = PWMOutputDevice(13)

print("Starting")

# Enable channels
pump_enable.value = 1.0
tt_enable.value = 0.4

# Start motors
pump.forward()
tt_motor.forward()

sleep(5)

# Stop motors
pump.stop()
tt_motor.stop()

# Disable channels
pump_enable.value = 0
tt_enable.value = 0

print("Done")