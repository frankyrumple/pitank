import RPi.GPIO as GPIO
import time
import os
from pyPS4Controller.controller import Controller

# GPIO Pins for power control
# Left Side
in1 = 6
in2 = 13
en1 = 5

# Right Side
in3 = 19
in4 = 26
en2 = 0


joy_path = "/dev/input/js0"


def js_connect():
    print("PS4 Controller Connected")
    pass

def js_disconnect():
    print("PS4 Controller Disconnected")
    pass


class Tank(Controller):
    # When to go low, med, or high
    LOW_THRESHOLD = 7000
    HIGH_THRESHOLD = 25000

    # Speeds for GPIO
    LOW = 50
    MED = 75
    HIGH = 100

    # PWM Value
    PWM = 100

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.left_track = 0
        self.right_track = 0
        self.left_track_motor = None
        self.right_track_motor = None
        self.init_gpio()

    def init_gpio(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(in1,GPIO.OUT)
        GPIO.setup(in2,GPIO.OUT)
        GPIO.setup(in3,GPIO.OUT)
        GPIO.setup(in4,GPIO.OUT)

        GPIO.setup(en1,GPIO.OUT)
        GPIO.setup(en2,GPIO.OUT)

        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        GPIO.output(in3,GPIO.LOW)
        GPIO.output(in4,GPIO.LOW)

        self.left_track_motor=GPIO.PWM(en1,Tank.PWM)
        self.left_track_motor.start(Tank.LOW)
        self.right_track_motor=GPIO.PWM(en2,Tank.PWM)
        self.right_track_motor.start(Tank.LOW)

    # Hide messages in base class
    def on_L3_right(self, value): pass
    def on_L3_left(self, value): pass
    def on_R3_right(self, value): pass
    def on_R3_left(self, value): pass
    def on_L3_x_at_rest(self): pass
    def on_R3_x_at_rest(self): pass


    def on_L3_up(self, value):
        value = abs(value)
        speed = 0
        if value > 0 and value < Tank.LOW_THRESHOLD:
            speed = Tank.LOW * -1
        elif value >= Tank.LOW_THRESHOLD and value < Tank.HIGH_THRESHOLD:
            speed = Tank.MED * -1
        elif value >= Tank.HIGH_THRESHOLD:
            speed = Tank.HIGH * -1

        self.left_track = speed
        self.set_speed()

    def on_L3_down(self, value):
        value = abs(value)
        speed = 0
        if value > 0 and value < Tank.LOW_THRESHOLD:
            speed = Tank.LOW
        elif value >= Tank.LOW_THRESHOLD and value < Tank.HIGH_THRESHOLD:
            speed = Tank.MED
        elif value >= Tank.HIGH_THRESHOLD:
            speed = Tank.HIGH

        self.left_track = speed
        self.set_speed()

    def on_L3_y_at_rest(self):
        self.left_track = 0
        self.set_speed()

    def on_R3_up(self, value):
        value = abs(value)
        speed = 0
        if value > 0 and value < Tank.LOW_THRESHOLD:
            speed = Tank.LOW * -1
        elif value >= Tank.LOW_THRESHOLD and value < Tank.HIGH_THRESHOLD:
            speed = Tank.MED * -1
        elif value >= Tank.HIGH_THRESHOLD:
            speed = Tank.HIGH * -1

        self.right_track = speed
        self.set_speed()

    def on_R3_down(self, value):
        value = abs(value)
        speed = 0
        if value > 0 and value < Tank.LOW_THRESHOLD:
            speed = Tank.LOW
        elif value >= Tank.LOW_THRESHOLD and value < Tank.HIGH_THRESHOLD:
            speed = Tank.MED
        elif value >= Tank.HIGH_THRESHOLD:
            speed = Tank.HIGH

        self.right_track = speed
        self.set_speed()

    def on_R3_y_at_rest(self):
        self.right_track = 0
        self.set_speed()

    def set_speed(self):
        # Use the current speed to drive the motors

        if self.left_track == 0:
            # Stop the track
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.LOW)
            print("L Stop")
        else:
            # Moving either forward or backwards
            abs_speed = abs(self.left_track)
            self.left_track_motor.ChangeDutyCycle(abs_speed)
            if self.left_track > 0:
                # Move backwards
                GPIO.output(in1,GPIO.LOW)
                GPIO.output(in2,GPIO.HIGH)
                print("L Back")
            else:
                # Move forwards
                GPIO.output(in1,GPIO.HIGH)
                GPIO.output(in2,GPIO.LOW)
                print("L Forward")


        if self.right_track == 0:
            # Stop the track
            GPIO.output(in3,GPIO.LOW)
            GPIO.output(in4,GPIO.LOW)
            print("R Stop")
        else:
            # Moving either forward or backwards
            abs_speed = abs(self.right_track)
            self.right_track_motor.ChangeDutyCycle(abs_speed)
            if self.right_track > 0:
                # Move backwards
                GPIO.output(in3,GPIO.LOW)
                GPIO.output(in4,GPIO.HIGH)
                print("R Back")
            else:
                # Move forwards
                GPIO.output(in3,GPIO.HIGH)
                GPIO.output(in4,GPIO.LOW)
                print("R Forward")





tank = Tank(interface=joy_path, connecting_using_ds4drv=False)
tank.debug = False


# Start the controller
tank.listen(timeout=300)

GPIO.cleanup()

