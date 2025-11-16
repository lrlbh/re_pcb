from machine import ADC

def ADC_AVG(pin_adc:ADC,n):
    uv = 0
    for _ in range(0,n):
        uv+= pin_adc.read_uv()
    return uv / n

def ADCS_AVG(pin_adcs,n):
    ret = [0] * len(pin_adcs)
    for _ in range(0,n):
        for i, pin_adc in enumerate(pin_adcs):
            ret[i]+= pin_adc.read_uv()
            
    for i in range(len(ret)):
        ret[i] /= n  
        
    return ret

class 环形List:
    def __init__(self, size,type = [0]):
        self._buf = type * size
        self._size = size
        self._write_idx = 0
        self._is_full = False
        self.latest = 0

    def append(self, value: int):
        self._buf[self._write_idx] = value
        self.latest = value
        self._write_idx = (self._write_idx + 1) % self._size
        if self._write_idx == 0:
            self._is_full = True

    def get_new(self):
        return self.latest

    def get_all(self):
        if not self._is_full:
            return self._buf[:self._write_idx]
        else:
            return self._buf[self._write_idx:] + self._buf[:self._write_idx]

