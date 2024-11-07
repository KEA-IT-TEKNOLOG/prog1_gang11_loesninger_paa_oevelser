# A simple potmeter test program
from machine import ADC, Pin
from time import sleep
from gpio_lcd import GpioLcd

# Create the LCD object
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32), d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)



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

lcd.putstr('BATTERY PERCENTAGE:')

previous_battery_percent = 0

while True:
    val = potmeter_adc.read()
    battery_percent = batt_percentage(batt_voltage(val))
    print('U percentage', battery_percent)
    if previous_battery_percent != battery_percent:
        lcd.move_to(0, 1)
        lcd.putstr(f"     ") # clear characters
        lcd.move_to(0, 1)
        lcd.putstr(f"{str(int(battery_percent))}%")
        previous_battery_percent = battery_percent
    sleep(0.2)