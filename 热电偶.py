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
from lib import ntc
# import socket


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
            # udp.send(f"标定成功：满量程输出{CG.TEMP.满量程read_uv}")
            break

    # 0飘，先简单在开机时校准
    await CG.TEMP.adj()

    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 重复测试温度
    while True:
        # 设计了3路热电偶，正常只使用1路，所以使用温度最高的热电耦即可
        # 这一坨输出没有冷端补偿的温度
        temp_3 = []
        for index, k in enumerate(CG.Pin.k_adc):
            原始读数 = k.read_uv()
            校准零飘后 = 原始读数 - CG.TEMP.k_零飘[index]
            pga后 = 校准零飘后 / CG.TEMP._PGA
            temp_3.append(CG.TEMP.get_temp(pga后))

        # 抛弃断线数据，然后计算平均值
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
        CG.TEMP.ntc_temp = temp.read(1)
        for i in range(len(temp_3)):
            temp_3[i] += CG.TEMP.ntc_temp
        CG.TEMP.热电耦平均温度[0] += CG.TEMP.ntc_temp
        CG.TEMP.热电耦平均温度[1] = time.ticks_ms()

        # # =========上位机测试=========
        # data = f"{CG.TEMP.热电耦平均温度[0]},{CG.TEMP.热电耦平均温度[1]}".encode(
        #     "utf-8"
        # )
        # sock.sendto(data, ("192.168.1.7", 1111))
        # # =========上位机测试=========

        # 滤波
        CG.TEMP.热电耦平均温度[0] = CG.TEMP.卡尔曼滤波器.get_data(
            CG.TEMP.热电耦平均温度[0]
        )
        # udp.send(CG.TEMP.热电耦平均温度[0] )

        # 存入环形内存
        temp_3.append(time.ticks_ms())
        CG.TEMP.热电耦温度.append(tuple(temp_3))

        if CG.WORK.work:
            await asyncio.sleep_ms(CG.TEMP._工作采样间隔MS)
        else:
            await asyncio.sleep_ms(CG.TEMP._非工作采样间隔MS)
