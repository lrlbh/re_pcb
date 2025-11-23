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
import sys
import io


async def work():
    # 放大倍数
    pga = 80

    # ntc对象
    temp = ntc.NTC(CG.Pin.k_ntc, 430_000, 3_300_000)

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
    await CG.TEMP.adj(pga, get_temp)

    # 重复测试温度
    while True:
        # 设计了3路热电偶，正常只使用1路，所以使用温度最高的热电耦即可
        # 这一坨输出没有冷端补偿的温度
        temp_3 = []
        for index, k in enumerate(CG.Pin.k_adc):
            原始读数 = tools.ADC_AVG(k, CG.TEMP._采样次数)
            校准零飘后 = 原始读数 - CG.TEMP.k_零飘[index]
            pga后 = 校准零飘后 / pga
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


async def run():
    try:
        await work()
    except Exception as e:
        # 捕获完整异常信息（含文件名、行号）
        buf = io.StringIO()
        sys.print_exception(e, buf)
        text = buf.getvalue()
        udp.send("=== 异常捕获 ===")
        udp.send(text)


# K型热电耦，电压转温度
def get_temp(uv):
    """
    将 K 型热电偶的补偿电势(μV) 转换为温度(°C)
    uv: 冷端已补偿后的总热电势（单位：μV）
    返回：热端温度（°C）
    """
    if uv < -5891 or uv > 54886:
        return 1000000

    # 3 段区间对应的逆多项式（ITS-90 标准）
    if uv < 0.0:
        d = [
            0.0000000e00,
            2.5173462e-02,
            -1.1662878e-06,
            -1.0833638e-09,
            -8.9773540e-13,
            -3.7342377e-16,
            -8.6632643e-20,
            -1.0450598e-23,
            -5.1920577e-29,
        ]
    elif uv <= 20644.0:
        d = [
            0.0000000e00,
            2.508355e-02,
            7.860106e-08,
            -2.503131e-10,
            8.315270e-14,
            -1.228034e-17,
            9.804036e-22,
            -4.413030e-26,
            1.057734e-30,
            -1.052755e-35,
        ]
    else:
        d = [
            -1.318058e02,
            4.830222e-02,
            -1.646031e-06,
            5.464731e-11,
            -9.650715e-16,
            8.802193e-21,
            -3.110810e-26,
        ]

    # Horner 计算温度（°C）
    t = 0.0
    for coef in reversed(d):
        t = t * uv + coef
    return t
