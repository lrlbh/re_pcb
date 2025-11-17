import asyncio
from lib import udp
from llib.config import CG
from llib import tools



async def run():
   
    # 灵敏度uv(满量程输出) / 量程克(10KG=20斤) * 放大倍数
    # 传感器描述里面误差基本来自这里，这里可以使用校准后的参数
    每克电压uv = 3300 / (500 * 20) * 101
    
    # 0飘 暂时为开始时校准
    零飘uv = tools.ADC_AVG(CG.Pin.kg_adc,CG.频率.KG校准次数)
    
    # 传感器上面的物体重量
    自重克 = 280

    while True:
        # 读取电压
        adc_uv = tools.ADC_AVG(CG.Pin.kg_adc,CG.频率.KG采样次数)
        # 计算克数
        CG.mem_data.kg.append_time(
            (adc_uv-零飘uv)   / 每克电压uv + 自重克)
        
        # udp.send(  Config.共享数据.kg.get_new())
        await asyncio.sleep_ms(CG.频率.KG采样间隔MS)