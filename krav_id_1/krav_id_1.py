from machine import Pin, PWM

###########################################################
# CONFIGURATION
# Rotary encoder pins, actual A or B depends the rotary encoder hardware. If backwards swap the pin numpers
pin_enc_a = 36
pin_enc_b = 39

#########################################################################
# OBJECTS
rotenc_a = Pin(pin_enc_a, Pin.IN, Pin.PULL_UP)
rotenc_B = Pin(pin_enc_b, Pin.IN, Pin.PULL_UP)

#########################################################################
# VARIABLES and CONSTANTS
enc_state = 0                          # Encoder state control variable

counter = 0                            # A counter that is incremented/decremented vs rotation

CW = 1                                 # Constant clock wise rotation
CCW = -1                               # Constant counter clock wise rotation

###########################################################
# FUNCTIONS
# Rotary encoder truth table, which one to use depends the actual rotary encoder hardware

def re_full_step():
    global enc_state

    encTableFullStep = [
        [0x00, 0x02, 0x04, 0x00],
        [0x03, 0x00, 0x01, 0x10],
        [0x03, 0x02, 0x00, 0x00],
        [0x03, 0x02, 0x01, 0x00],
        [0x06, 0x00, 0x04, 0x00],
        [0x06, 0x05, 0x00, 0x20],
        [0x06, 0x05, 0x04, 0x00]]

    enc_state = encTableFullStep[enc_state & 0x0F][(rotenc_B.value() << 1) | rotenc_a.value()]
 
    # -1: Left/CCW, 0: No rotation, 1: Right/CW
    result = enc_state & 0x30
    if (result == 0x10):
        return CW
    elif (result == 0x20):
        return CCW
    else:
        return 0


# Move connector on JP13 to the right to control LCD brightness with PWM
# CONNECT: JP6 GP5 -> JP1 MOSI (To bypass port expander and control LCD brightness with PWM)
brightness_PWM = PWM(Pin(13, Pin.OUT))
brightness_PWM.duty(1)


while True:
    # Read the rotary encoder
    res = re_full_step()               # or: re_half_step()

    if res == CW:
        if counter > 9: #set counter max value to 10
            counter = 10
        else:
            counter += res            
        print(f"Right/CW: {counter}")
        brightness_PWM.duty(int(counter * 102.3))
        print(f"Counter multiplied value: {int(counter * 102.3)}")
            
    if res == CCW:
        if counter < 1: #set counter min value to 0
            counter = 0
        else:
            counter += res
        print(f"Left/CWW: {counter}")
        print(f"Counter multiplied value: {int(counter * 102.3)}")
        brightness_PWM.duty(int(counter * 102.3))