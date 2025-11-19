import asyncio
from lib import Fan
from llib.config import CG

async def run():

    zs = Fan.Fan(CG.Pin.fan_fead)
    while True:
        CG.Pin.fan_pwm.duty_u16(CG.mem.fan_pwm)
        CG.mem.fan_read.append_time(zs.read())
        await asyncio.sleep_ms(CG.频率.风扇采样间隔)
