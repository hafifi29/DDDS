import time
# import RPi.GPIO as GPIO
import winsound

BUZZER_PIN = 18

def start_alarm(alarm_status):
    """Activate the buzzer when drowsiness is detected."""
    while alarm_status:
        winsound.Beep(1000,500)
        # power_buzzer_on()
        # time.sleep(0.5)

        # power_buzzer_off
        # time.sleep(0.5)

def power_buzzer_off():
    pass
    # GPIO.output(BUZZER_PIN, GPIO.LOW)

def power_buzzer_on():
    pass
    # GPIO.output(BUZZER_PIN, GPIO.HIGH)

def clean_pins_up():
    pass
    # GPIO.cleanup()