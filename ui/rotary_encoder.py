import RPi.GPIO as GPIO


class RotaryEncoder:
    def __init__(self, pin_a, pin_b, button_pin):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.button_pin = button_pin

        # Set up GPIO mode and pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_a, GPIO.IN)
        GPIO.setup(self.pin_b, GPIO.IN)
        GPIO.setup(self.button_pin, GPIO.IN)

        # Variables to track state and position
        self.last_state = None
        self.position = 0
        self.button_pressed = False

    def update_position(self):
        pin_a_state = GPIO.input(self.pin_a)
        pin_b_state = GPIO.input(self.pin_b)

        if pin_a_state != self.last_state:
            if pin_a_state == 0:
                if pin_b_state == 1:
                    self.position += 1
                else:
                    self.position -= 1

        self.last_state = pin_a_state

    def select_button_pressed(self):
        self.button_pressed = True

    def clear_button_pressed(self):
        self.button_pressed = False

    def setup_rotary_encoder(self):
        # Set up interrupt handlers for the rotary encoder pins
        GPIO.add_event_detect(
            self.pin_a,
            GPIO.RISING,
            callback=self.update_position)
        GPIO.add_event_detect(
            self.button_pin,
            GPIO.FALLING,
            callback=self.select_button_pressed)
