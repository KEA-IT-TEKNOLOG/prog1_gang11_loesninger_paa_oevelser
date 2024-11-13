from uthingsboard.client import TBDeviceMqttClient
from time import ticks_ms
from machine import reset, ADC, Pin
import gc
import secrets

potmeter_adc = ADC(Pin(34))
potmeter_adc.atten(ADC.ATTN_11DB) # Full range: 3,3 V and 12 bits

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
client.connect() # Connecting to ThingsBoard
print("connected to thingsboard, starting to send and receive data")


start = ticks_ms()
delay = 20000 # delay to send telemetry
while True:
    try:
        if ticks_ms() - start > delay:            
            print(f"free memory: {gc.mem_free()}") # monitor memory left
            if gc.mem_free() < 2000: # free memory if below 2000 bytes left
                print("Garbage collected!")
                gc.collect() # free memory 
            
            val = potmeter_adc.read()
            battery_percent = batt_percentage(batt_voltage(val))
                                 
            telemetry = {"battery percentage" : battery_percent} # store telemetry in dictionary     
            client.send_telemetry(telemetry) #Sending telemetry  
            start = ticks_ms()
    except KeyboardInterrupt:
        print("Disconnected!")
        client.disconnect() # Disconnecting from ThingsBoard
        reset() # reset ESP32

        