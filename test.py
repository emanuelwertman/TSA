from gpiozero import Motor, PMOutputDevice
from time import sleep

pump = Motor(forward=20, backward=21)
enb = PWMOutputDevice(13)

print("Pump On")
enb.value = 1.0
pump.forward()

sleep(15)

pump.stop()
enb.value = 0
print("Done")