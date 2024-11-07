from uthingsboard.client import TBDeviceMqttClient
from time import ticks_ms
from machine import reset, ADC, Pin, PWM
import gc
import secrets
from gpio_lcd import GpioLcd
from rotary_encoder import RotaryEncoder


# Create the RotaryEncoder object
rotary_enc = RotaryEncoder()

# Create the LCD object
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32), d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

# Move connector on JP13 to the right to control LCD brightness with PWM
# CONNECT: JP6 GP5 -> JP1 MOSI (To bypass port expander and control LCD brightness with PWM)
brightness_PWM = PWM(Pin(13, Pin.OUT))
brightness_PWM.duty(512)


potmeter_adc = ADC(Pin(34))
potmeter_adc.atten(ADC.ATTN_11DB)      # Full range: 3,3 V and 12 bits

adc1 = 2390
U1 = 4.1
adc2 = 2080
U2 = 3.6

a = (U1-U2)/(adc1-adc2)
b = U2 - a*adc2

def batt_voltage(adc_v):
    u_batt = a*adc_v+b
    return u_batt

#Procent:
# 3V = 0%
# 4.2V = 100%
def batt_percentage(u_batt):
    without_offset = (u_batt-3)
    normalized = without_offset / (4.2-3.0)
    percent = normalized * 100
    return percent

# Make client object to connect to thingsboard
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token = secrets.ACCESS_TOKEN)
client.connect()                           # Connecting to ThingsBoard
print("connected to thingsboard, starting to send and receive data")


start_telemetry = ticks_ms()
delay_telemetry = 20000 # delay to send telemetry once every second

start_display = ticks_ms()
delay_display = 200

lcd.putstr('BATTERY PERCENTAGE:')
previous_battery_percent = 0

while True:
    try:
        if ticks_ms() - start_display > delay_display:
            val = potmeter_adc.read()
            battery_percent = int(batt_percentage(batt_voltage(val)))
            if previous_battery_percent != battery_percent:
                print('U percentage', battery_percent)
                lcd.move_to(0, 1)
                lcd.putstr(f"     ") # clear characters
                lcd.move_to(0, 1)
                lcd.putstr(f"{str(int(battery_percent))}%")
                previous_battery_percent = battery_percent
            start_display = ticks_ms()
            
        if ticks_ms() - start_telemetry > delay_telemetry:            
            print(f"free memory: {gc.mem_free()}") # monitor memory left
            if gc.mem_free() < 2000:          # free memory if below 2000 bytes left
                print("Garbage collected!")
                gc.collect()                  # free memory 
            print(f"Sending battery percentage: {battery_percent}%")                  
            telemetry = {"battery percentage" : battery_percent}                # store telemetry in dictionary     
            client.send_telemetry(telemetry) #Sending telemetry  
            start_telemetry = ticks_ms()
    
        # Read the rotary encoder
        res = rotary_enc.re_full_step()

        if res == rotary_enc.CW:
            if rotary_enc.counter > 9: #set counter max value to 10
                rotary_enc.counter = 10
            else:
                rotary_enc.counter += res            
            print(f"Right/CW: {rotary_enc.counter}")
            brightness_PWM.duty(int(rotary_enc.counter * 102.3))
            print(f"Counter multiplied value: {int(rotary_enc.counter * 102.3)}")
                
        if res == rotary_enc.CCW:
            if  rotary_enc.counter < 1: #set counter min value to 0
                 rotary_enc.counter = 0
            else:
                 rotary_enc.counter += res
            print(f"Left/CWW: {rotary_enc.counter}")
            print(f"Counter multiplied value: {int(rotary_enc.counter * 102.3)}")
            brightness_PWM.duty(int(rotary_enc.counter * 102.3))
            

    except KeyboardInterrupt:
        print("Disconnected!")
        client.disconnect()               # Disconnecting from ThingsBoard
        reset()                           # reset ESP32

        