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

IN3 = 38
IN4 = 40
ENB = 33

# Setup GPIO mode
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Initialize PWM on ENA pin at 100Hz frequency
pwm1 = GPIO.PWM(ENA, 500)
pwm1.start(0)  # Start with 0% duty cycle (Off)
pwm2 = GPIO.PWM(ENB, 500)
pwm2.start(0)

try:
    print("Pump On")
    
    # Establish direction: IN1 High and IN2 Low for forward
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    
    pwm1.ChangeDutyCycle(100)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(100)

    # Run for 5 seconds
    sleep(5)

finally:
    # Stop the pump and clean up the pins safely
    print("Done")

    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    
    pwm1.ChangeDutyCycle(0)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm2.ChangeDutyCycle(0)

    pwm1.stop()
    pwm2.stop()

    GPIO.cleanup()