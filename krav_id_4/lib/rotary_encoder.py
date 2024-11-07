from machine import Pin

###########################################################
# CONFIGURATION
# Rotary encoder pins, actual A or B depends the rotary encoder hardware. If backwards swap the pin numpers
class RotaryEncoder:
    def __init__(self, pin_enc_a = 36, pin_enc_b = 39):
        self.rotenc_a = Pin(pin_enc_a, Pin.IN, Pin.PULL_UP)
        self.rotenc_b = Pin(pin_enc_b, Pin.IN, Pin.PULL_UP)
        self.enc_state = 0                          
        self.counter = 0                            
        self.CW = 1                                 
        self.CCW = -1  
                

    def re_full_step(self):
        
        encTableFullStep = [
            [0x00, 0x02, 0x04, 0x00],
            [0x03, 0x00, 0x01, 0x10],
            [0x03, 0x02, 0x00, 0x00],
            [0x03, 0x02, 0x01, 0x00],
            [0x06, 0x00, 0x04, 0x00],
            [0x06, 0x05, 0x00, 0x20],
            [0x06, 0x05, 0x04, 0x00]]

        self.enc_state = encTableFullStep[self.enc_state & 0x0F][(self.rotenc_b.value() << 1) | self.rotenc_a.value()]
     
        # -1: Left/CCW, 0: No rotation, 1: Right/CW
        result = self.enc_state & 0x30
        if result == 0x10:
            return self.CW
        elif result == 0x20:
            return self.CCW
        else:
            return 0
