from llib import  tools
from llib.config import CG
import asyncio
from lib import udp



async def run():
    while True:
        if CG.共享数据.热压:
            await work()
        else:
            await no_work()

        await asyncio.sleep_ms(300)


async def work():
    pwm = (CG.共享数据.热压目标温度 - CG.共享数据.热电耦合温度.get_new()) * 655
    pwm = int(pwm)
    if pwm > 65535:
        pwm = 65535
    elif pwm < 0:
        pwm = 0
    CG.Pin.pow_pwm.duty_u16(pwm)

    # kg_pwm = (CG.共享数据.热压目标压力 - CG.共享数据.kg.get_new()) * 131
    # kg_pwm = 65535 - int(kg_pwm)
    # if kg_pwm > 45000:
    #     kg_pwm = 65535
    # elif kg_pwm < 0:
    #     kg_pwm = 0
    # CG.Pin.m_pwm2.duty_u16(65535)
    # CG.Pin.m_pwm1.duty_u16(kg_pwm)

    udp.send(
        f"温度: {CG.共享数据.热电耦合温度.get_new():.2f}\t"
        f"kg: {CG.共享数据.kg.get_new():.0f}\t"
        f"加热电流: {CG.共享数据.功率片电流.get_new():.2f}\t"
        f"电机电流: {CG.共享数据.电机电流.get_new():.2f}\t"
        f"目标压力: {CG.共享数据.热压目标压力}"
        f"目标温度: {CG.共享数据.热压目标温度}"
        f"加热PWM: {pwm}"
    )


async def no_work():
    # pwm = 0
    # CG.Pin.m_pwm2.duty_u16(0)
    # CG.Pin.m_pwm1.duty_u16(65535)

    CG.Pin.pow_pwm.duty_u16(0)
    # if  CG.共享数据.电机电流.get_new() > 100:
    #     CG.Pin.m_pwm2.duty_u16(65535)
    #     CG.Pin.m_pwm1.duty_u16(65535)
    udp.send(
        f"温度: {CG.共享数据.热电耦合温度.get_new():.2f}\t"
        f"kg: {CG.共享数据.kg.get_new():.0f}\t"
        f"加热电流: {CG.共享数据.功率片电流.get_new():.2f}\t"
        f"电机电流: {CG.共享数据.电机电流.get_new():.2f}\t"
        f"风扇转速: {CG.共享数据.fan_read.get_new():.2f}\t"
        f"风扇PWM: {CG.共享数据.fan_pwm:.2f}\t"
        f"加热PWM: 0"
    )
