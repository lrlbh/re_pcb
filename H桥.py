import asyncio
from llib.config import CG
from llib import tools
from lib import udp


async def run():
    CG.H桥.adj()
    while True:
        uv = tools.ADC_AVG(CG.Pin.m_adc, CG.H桥._采样次数) - CG.H桥.零飘
        电流ma = uv / 20 / 50
        CG.H桥.电流.append_time(电流ma)
        # udp.send(f"电流:{电流ma}")
        await asyncio.sleep_ms(CG.H桥._采样间隔MS)
