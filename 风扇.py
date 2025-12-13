import asyncio
from lib import  tools
from llib.config import CG


@tools.catch_and_report("风扇采样任务")
async def run():
    while True:
        CG.FAN.fan_pwm.duty_u16(CG.WORK._fan_pwm)
        CG.FAN.fan_read.append_time(CG.FAN.fan_zs.read())
        await asyncio.sleep_ms(CG.FAN._采样间隔MS)
