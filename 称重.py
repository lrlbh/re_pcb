import asyncio
from lib import udp
from llib.config import CG
from llib import tools


async def run():
    # 灵敏度uv(满量程输出) / 量程克(10KG=20斤) * 放大倍数
    # 传感器描述里面误差基本来自这里，这里可以使用校准后的参数
    每克电压uv = 3300 / (500 * 20) * 101

    CG.adj.称重()

    while True:
        # 读取电压
        adc_uv = tools.ADC_AVG(CG.Pin.kg_adc, CG.频率.KG采样次数)
        # 计算克数
        CG.mem.kg.append_time((adc_uv - CG.mem.称重零飘) / 每克电压uv + CG.disk.自重克)

        # udp.send(  Config.共享数据.kg.get_new())
        await asyncio.sleep_ms(CG.频率.KG采样间隔MS)
