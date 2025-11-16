import time

from machine import Pin


class Fan:
    def __init__(self, pin):
        self.脉冲个数 = 0
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        # noinspection PyTypeChecker
        self.开始时间戳 = time.ticks_ms() / 1000
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=lambda p: self.tach_isr(p))

    def tach_isr(self, pin):
        self.脉冲个数 += 1

    # 默认，两个脉冲一圈，多少秒的圈速
    def read(self, 几个脉冲一圈=2, 时间单位=60):
        # 两次读取间隔
        # noinspection PyTypeChecker
        间隔 = time.ticks_ms() / 1000 - self.开始时间戳
        if 间隔 <= 0:
            return 0

        # 每分钟转速
        分钟转速 = self.脉冲个数 / 几个脉冲一圈 * (时间单位 / 间隔)

        # 重置时间和脉冲
        self.脉冲个数 = 0
        # noinspection PyTypeChecker
        self.开始时间戳 = time.ticks_ms() / 1000

        # 四舍五入，保留两个小数 # return round(分钟转速, 2)
        # 舍弃小数
        return int(分钟转速 * 100) / 100
