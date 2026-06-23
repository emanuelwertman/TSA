import gpiod
from time import sleep

# Define the Broadcom (BCM) GPIO numbers
IN1_PIN = 5
IN2_PIN = 6

print("Pump On")

# Request access to the main GPIO chip (usually chip 0)
with gpiod.request_lines(
    "/dev/gpiochip0",
    consumer="pump-control",
    config={
        IN1_PIN: gpiod.LineSettings(direction=gpiod.Direction.OUTPUT, output_value=gpiod.Value.ACTIVE),
        IN2_PIN: gpiod.LineSettings(direction=gpiod.Direction.OUTPUT, output_value=gpiod.Value.INACTIVE),
    },
) as lines:

    # Note: Software PWM is not natively handled well by raw gpiod.
    # If your pump requires a full 100% duty cycle to just turn on, 
    # you can wire the ENA pin directly to a physical 3.3V or 5V pin,
    # or add ENA to the lines config above as ACTIVE.

    sleep(15)

print("Done")