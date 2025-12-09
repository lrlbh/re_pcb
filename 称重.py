import asyncio
from llib.config import CG
from lib import tools, udp


@tools.catch_and_report("KG采样任务")
async def run():
    CG.KG.adj()

    while True:
        # 读取电压
        adc_uv = tools.ADC_AVG(CG.Pin.kg_adc, CG.KG._采样次数)
        # 计算克数
        CG.KG.kg.append_time(
            (adc_uv - CG.KG.称重零飘) / CG.KG.每克电压uv + CG.KG._自重克
        )

        # udp.send(CG.KG.kg.get_new()[0])
        await asyncio.sleep_ms(CG.KG._采样间隔MS)
