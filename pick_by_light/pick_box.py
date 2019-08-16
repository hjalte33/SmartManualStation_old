

class PickBox:
    def __init__ (self, pir_pin, led_pin, position_id)
        self.position_id = position_id
        self.pir_pin = pir_pin
        self.led_pin = led_pin

        GPIO.setup(self.pir_pin, GPIO.IN)
        GPIO.setup(self.led_pin, GPIO.OUT)

    def set_content(self, content_id):
        pass
    
    def get_content(self):
        return True #the content

    def