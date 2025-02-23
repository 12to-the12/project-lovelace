from machine import PWM

beeper = PWM(13)


def lcd_start_tone(frequency, volume):
    beeper.freq(frequency)  # Set the frequency
    beeper.duty_u16(volume)  # Set the duty cycle (0 to 1023 for 10-bit resolution)


def lcd_stop_tone():
    beeper.duty_u16(0)  # Turn off the beeper after the duration
