
class BatteryPercent:
    def __init__(self, adc1 = 2390, U1 = 4.1, adc2 = 2080, U2 = 3.6):
        self.adc1 = adc1
        self.U1 = U1
        self.adc2 = adc2
        self.U2 = U2
        self.a = (self.U1 - self.U2) / (self.adc1 - self.adc2)
        self.b = self.U2 - self.a * self.adc2

    def batt_voltage(self, adc_v):
        u_batt = self.a * adc_v + self.b
        return u_batt

    #Procent:
    # 3V = 0%
    # 4.2V = 100%
    def batt_percentage(self, u_batt):
        without_offset = (u_batt-3)
        normalized = without_offset / (4.2-3.0)
        percent = normalized * 100
        return percent


