import RPi.GPIO as GPIO
from time import sleep

# Use physical Pin numbers (BOARD) or Broadcom GPIO numbers (BCM)
# Based on your pinout, we will use BCM numbering:
# GPIO5  -> IN1 (Pin 29)
# GPIO6  -> IN2 (Pin 31)
# GPIO12 -> ENA (Pin 32)

IN1 = 29
IN2 = 31
ENA = 32

# Setup GPIO mode
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Initialize PWM on ENA pin at 100Hz frequency
pwm = GPIO.PWM(ENA, 1000)
pwm.start(0)  # Start with 0% duty cycle (Off)

try:
    print("Pump On")
    
    # Set the speed to 100% (Duty cycle ranges from 0.0 to 100.0 in RPi.GPIO)
    pwm.ChangeDutyCycle(100)
    
    # Establish direction: IN1 High and IN2 Low for forward
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    
    # Run for 15 seconds
    sleep(15)

finally:
    # Stop the pump and clean up the pins safely
    print("Done")
    pwm.stop()
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.cleanup()