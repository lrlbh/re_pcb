# 此乃有效测量范围，非实际测量范围，代表建议使用该范围
# • 当 ATTEN=0，有效测量范围为 0 ~ 750 mV 时，总误差为 ±10 mV。
# • 当 ATTEN=1，有效测量范围为 0 ~ 1050 mV 时，总误差为 ±10 mV。
# • 当 ATTEN=2，有效测量范围为 0 ~ 1300 mV 时，总误差为 ±10 mV。
# • 当 ATTEN=3，有效测量范围为 0 ~ 2500 mV 时，总误差为 ±35 mV。

# 实际范围
# • 当 ATTEN=0，有效测量范围为 0 ~ 845 mV 时
# • 当 ATTEN=1，有效测量范围为 0 ~ 1133 mV 时
# • 当 ATTEN=2，有效测量范围为 0 ~ 1565 mV 时
# • 当 ATTEN=3，有效测量范围为 0 ~ 2865 mV 时

# ADC.ATTN_0DB
# ADC.ATTN_2_5DB
# ADC.ATTN_6DB
# ADC.ATTN_11DB


from lib import udp
import asyncio
from llib.config import CG, temp_data
from llib import tools


async def run():
    while True:
        ret = tools.ADCS_AVG([CG.Pin.pow_adc, CG.Pin.v_adc], CG.频率.POW采样次数)
        电流 = ret[0]
        电流 -= CG.mem.电流零飘
        电流 /= 1000_000  # 单位V
        电流 /= 100  # 放大倍数
        电流 /= 0.0003  # 阻值
        电流 /= 1  # 线性误差
        CG.mem.电流.append_time(电流)
        电压 = ret[1]
        电压 *= 33
        电压 /= 1000_000
        CG.mem.输入电压.append_time(电压)
        
        temp_data.st波形.append_data(
            [
                电压,
                CG.Pin.pow_pwm.duty_100(),
                CG.mem.热电耦平均温度[0],
                电流,
            ]
        )

        await asyncio.sleep_ms(CG.频率.POW采样间隔MS)
