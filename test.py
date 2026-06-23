import gpiod
from time import sleep

IN1_PIN = 5
IN2_PIN = 6
ENA_PIN = 12

print("Pump On")

# Open the GPIO chip
chip = gpiod.Chip('gpiochip0')

# Get the lines for our pins
lines = chip.get_lines([IN1_PIN, IN2_PIN, ENA_PIN])

# Request the lines as outputs
lines.request(consumer="pump-control", type=gpiod.LINE_REQ_DIR_OUT)

try:
    # Set IN1 to High (1), IN2 to Low (0) for forward
    # Set ENA to High (1) to enable the motor driver channel
    lines.set_values([1, 0, 1])
    
    sleep(15)

finally:
    # Turn everything off when done
    print("Done")
    lines.set_values([0, 0, 0])
    lines.release()
    chip.close()