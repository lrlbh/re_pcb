import asyncio
from llib.config import CG
from llib import tools
from lib import udp


async def run():
    CG.adj.电机()
    while True:
        uv = tools.ADC_AVG(CG.Pin.m_adc, CG.频率.H桥样次数) - CG.mem.电机零飘
        电流ma = uv / 20 / 50
        CG.mem.电机电流.append_time(电流ma)
        # udp.send(f"电流:{电流ma}")
        await asyncio.sleep_ms(CG.频率.H桥样间隔MS)
