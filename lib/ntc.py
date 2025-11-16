from machine import ADC
from 热敏电阻型号 import 型号


class NTC:
    def __init__(
        self,
        adc_对象: ADC,
        固定电阻=430_000,
        电路电压uv=3_300_000,
        型号_t=型号.瑞隆_50K_4150,
    ):
        self.adc = adc_对象
        self.电路电压uv = 电路电压uv
        self.固定电阻 = 固定电阻
        self.型号 = 型号_t

    def read(self):
        NTC的电压 = self.adc.read_uv() 
        固定电阻的电压 = self.电路电压uv - NTC的电压
        电流 = 固定电阻的电压 / self.固定电阻
        NTC的电阻 = NTC的电压 / 电流 / 1000
        # return NTC的电阻

        for i, 阻值 in enumerate(self.型号.阻值):
            if 阻值 <= NTC的电阻:
                # 和上一个阻值的间隔
                阻值间隔 = 阻值 - self.型号.阻值[i - 1]
                # 当前温度剩余的阻值
                剩余阻值 = 阻值 - NTC的电阻
                # 简单计算一下线性百分比
                百分比温度 = 剩余阻值 / 阻值间隔
                温度 = i + self.型号.起始温度 - 百分比温度

                # 四舍五入，保留两个小数
                # return round(温度, 2)
                return int(温度 * 100) / 100
