from machine import PWM
from config import config




class Buzzer:
    def __init__(self):
        self.duty = 0
        self.PWM = PWM(13)
        self.max_volume = config.max_volume

    def set(self, freq, volume):
        if volume > self.max_volume:
            self.volume = self.max_volume
        try:
            self.PWM.freq(int(freq))
        except:
            pass
        self.freq = freq
        self.PWM.duty_u16(int(volume))
        self.volume = volume

    def stop(self):
        self.set(0, 0)


buzzer = Buzzer()
