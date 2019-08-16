import RPi.GPIO as GPIO

if not GPIO.getmode():
    GPIO.setmode(BCM)