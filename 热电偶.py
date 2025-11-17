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

import asyncio
from llib.config import CG, tools
from lib import udp, ntc





# 短路校准
# -----------------
# 热电耦合测量的是冷端和探头的温差
# 为了避免校准时，冷热端温度不一样，可以短路冷端输入信号
# 然后在校准运放0飘
# -----------------
# 当然这也会引入两个问题
# 1、共模电压改变，不过共模电压主要来自K_REF,影响很小
# 2、MOS内阻，这是主要问题，可以选择低VGSth，低内阻MOS
async def 短路校准():
    K_零点 = []
    CG.Pin.k_sw.value(1)
    await asyncio.sleep(0.2)

    # 遍历 ADC
    for k in CG.Pin.k_adc:
        K_零点.append(tools.ADC_AVG(k, CG.频率.K采样校准次数))

    CG.Pin.k_sw.value(0)

    return K_零点


async def run():
    # Config.Pin.k_sw.value(0)
    # while True:
    #     await asyncio.sleep_ms(Config.频率.K采样间隔MS)
    
    
    # 放大倍数
    pga = 100
    
    # ntc对象
    temp = ntc.NTC(CG.Pin.k_ntc, 430_000,3_300_000)
    
    # 0飘，先简单在开机时校准
    k_零点 = await 短路校准()
    
    # 重复测试温度
    while True:
        # 设计了3路热电偶，正常只使用1路，所以使用温度最高的热电耦即可
        k_max = -100000
        for index, k in enumerate(CG.Pin.k_adc):
            原始读数 = tools.ADC_AVG(k, CG.频率.K采样次数)
            校准零飘后 = 原始读数- k_零点[index]
            pga后 = 校准零飘后 / pga
            转为实际温度 = get_temp(pga后)
            # udp.send(转为实际温度)
            if 原始读数 > 900_000: # 大于900mv,属于短线检测
                continue
            if 转为实际温度 > k_max :
                k_max = 转为实际温度
        
        # 3个都短线，给予一个大的温度值                
        if k_max < -1000:
            k_max = 100000
        
        # 看看ntc温度要不要多测两次
        CG.mem_data.热电耦合温度.append_time(k_max+temp.read())
        
        # udp.send(CG.共享数据.热电耦合温度.get_new())
        
        await asyncio.sleep_ms(CG.频率.K采样间隔MS)

 
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