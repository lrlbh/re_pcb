# 此乃有效测量范围，非实际测量范围，代表建议使用该范围
# • 当 ATTEN=0，有效测量范围为 0 ~ 850 mV 时，总误差为 ±5 mV。
# • 当 ATTEN=1，有效测量范围为 0 ~ 1100 mV 时，总误差为 ±6 mV。
# • 当 ATTEN=2，有效测量范围为 0 ~ 1600 mV 时，总误差为 ±10 mV。
# • 当 ATTEN=3，有效测量范围为 0 ~ 2900 mV 时，总误差为 ±50 mV。

# 理论范围
# • 当 ATTEN=0，有效测量范围为 0 ~ 950 mV 时
# • 当 ATTEN=1，有效测量范围为 0 ~ 1250 mV 时
# • 当 ATTEN=2，有效测量范围为 0 ~ 1750 mV 时
# • 当 ATTEN=3，有效测量范围为 0 ~ 3100 mV 时

# ADC.ATTN_0DB
# ADC.ATTN_2_5DB
# ADC.ATTN_6DB
# ADC.ATTN_11DB

import time
import asyncio
from llib.config import CG, tools
from lib import udp, ntc


@tools.catch_and_report("热电耦采样任务")
async def run():


    # ntc对象
    temp = ntc.NTC(CG.Pin.k_ntc, CG.TEMP._R1阻值, CG.TEMP._输入电压uv)

    # 标定满量程 read_uv 输出
    # 如果热电耦合全被使用，提供一个def
    for k in CG.Pin.k_adc:
        t_16 = []
        t_uv = []
        for _ in range(3):
            t_16.append(k.read_u16())
            t_uv.append(k.read_uv())
        if max(t_16) == 65535:
            CG.TEMP.满量程read_uv = max(t_uv)
            udp.send(f"标定成功：满量程输出{CG.TEMP.满量程read_uv}")
            break

    # 0飘，先简单在开机时校准
    await CG.TEMP.adj(CG.TEMP._PGA, get_temp)

    # 重复测试温度
    while True:
        # 设计了3路热电偶，正常只使用1路，所以使用温度最高的热电耦即可
        # 这一坨输出没有冷端补偿的温度
        temp_3 = []
        for index, k in enumerate(CG.Pin.k_adc):
            原始读数 = tools.ADC_AVG(k, CG.TEMP._采样次数)
            校准零飘后 = 原始读数 - CG.TEMP.k_零飘[index]
            pga后 = 校准零飘后 / CG.TEMP._PGA
            temp_3.append(get_temp(pga后))
 
        # 抛弃断线，然后计算平均值 
        n = 0
        CG.TEMP.热电耦平均温度[0] = 0
        for i, temp_i in enumerate(temp_3):
            # 断线
            # 可以轻松几度
            if temp_i == CG.TEMP.k_max[i]:
                continue
            CG.TEMP.热电耦平均温度[0] += temp_i
            n += 1 
        if n > 0:
            CG.TEMP.热电耦平均温度[0] /= n
        else:
            CG.TEMP.热电耦平均温度[0] = 920

        # ntc温度
        CG.TEMP.ntc_temp = temp.read(100)
        for i in range(len(temp_3)):
            temp_3[i] += CG.TEMP.ntc_temp
        CG.TEMP.热电耦平均温度[0] += CG.TEMP.ntc_temp
        CG.TEMP.热电耦平均温度[1] = time.ticks_ms()

        # 存入环形内存
        temp_3.append(time.ticks_ms())
        CG.TEMP.热电耦温度.append(tuple(temp_3))

        await asyncio.sleep_ms(CG.TEMP._采样间隔MS)




def get_temp(uv: float) -> float:
    """
    把 Type-K 热电偶的电势（μV, cold-junction 已补偿后的总电势）转换成温度 (°C)
    uv: 电势，单位 microvolts (µV) --- *必须是 µV*
    返回：温度 (°C)。若超出 NIST 多项式定义域，返回 1_000_000 表示错误。
    系数来自 NIST / ITS-90 逆多项式（常见实现与文档一致）。
    """
    # 有效范围（µV）
    if uv < -5891.0 or uv > 54886.0:
        return 1_000_000.0

    # 逆多项式系数（按 NIST/ITS-90，输入 E 单位为 µV，输出为 °C）
    # 区间  : -200 .. 0 °C   对应电势约 -5891 .. 0 µV
    if uv < 0.0:
        c = [
            0.000000000000E+00,
            2.5949192E-02,
           -2.1312719E-07,
            7.9018692E-10,
            4.2527777E-13,
            1.3304473E-16,
            2.0241446E-20,
            1.2668171E-24,
           -1.3180580E-29,
            0.0000000E+00,
        ]
    # 区间 : 0 .. 500 °C   对应电势约 0 .. 20644 µV
    elif uv <= 20644.0:
        c = [
            0.000000000000E+00,
            2.508355E-02,
            7.860106E-08,
           -2.503131E-10,
            8.315270E-14,
           -1.228034E-17,
            9.804036E-22,
           -4.413030E-26,
            1.057734E-30,
           -1.052755E-35,
        ]
    # 区间 : 500 .. 1372 °C
    else:
        c = [
           -1.318058E+02,
            4.830222E-02,
           -1.646031E-06,
            5.464731E-11,
           -9.650715E-16,
            8.802193E-21,
           -3.110810E-26,
        ]

    # Horner 求值（从最高次项开始）
    t = c[-1]
    for coef in reversed(c[:-1]):
        t = t * uv + coef
    return t

