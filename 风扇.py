import asyncio
from lib import Fan,tools
from llib.config import CG

@tools.catch_and_report("风扇采样任务")
async def run():

    zs = Fan.Fan(CG.Pin.fan_fead)
    while True:
        CG.Pin.fan_pwm.duty_u16(CG.WORK._fan_pwm)
        CG.FAN.fan_read.append_time(zs.read())
        await asyncio.sleep_ms(CG.FAN._采样间隔MS)
