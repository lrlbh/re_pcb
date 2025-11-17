import asyncio
from llib.config import CG
from llib import tools
from lib import udp

async def run():
    零飘 = tools.ADC_AVG(CG.Pin.m_adc,CG.频率.H桥采样校准次数)
    # udp.send(f"零票:{零飘}")
    while True:
        uv = tools.ADC_AVG(CG.Pin.m_adc,CG.频率.H桥样次数) - 零飘
        电流ma = uv / 20 / 50
        CG.mem_data.电机电流.append_time(电流ma)
        # udp.send(f"电流:{电流ma}")
        await asyncio.sleep_ms(CG.频率.H桥样间隔MS) 
                                           
                                           
    