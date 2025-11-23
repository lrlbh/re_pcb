from machine import Pin, ADC, SPI
from llib import tools
from lib import pwm, lcd, disk_config
import time
import asyncio


class CG(disk_config.DiskConfig):
    class H桥:
        _校准次数 = 10_000
        _采样次数 = 100
        _采样间隔MS = 24
        _关闭电流MA = 104
        _保护电流MA = 600
        _关闭延迟S = 5

        零飘 = 0
        电流 = tools.环形List(60000, (0, time.ticks_ms()))

        @staticmethod
        def down():
            CG.Pin.m_pwm1.duty_u16(0)
            CG.Pin.m_pwm2.duty_u16(65535)

        @staticmethod
        def up():
            CG.Pin.m_pwm1.duty_u16(65535)
            CG.Pin.m_pwm2.duty_u16(0)

        @staticmethod
        def close():
            CG.Pin.m_pwm1.duty_u16(65535)
            CG.Pin.m_pwm2.duty_u16(65535)

        @staticmethod
        def adj():
            CG.H桥.零飘 = tools.ADC_AVG(CG.Pin.m_adc, CG.H桥._校准次数)

    class BMQ:
        _轮询间隔MS = 50
        _抖动等待MS = 10

    class KG:
        _校准次数 = 10_000
        _采样次数 = 100
        _采样间隔MS = 24
        _自重克 = 280
        kg = tools.环形List(60000, (0, time.ticks_ms()))
        称重零飘 = 0

        @staticmethod
        def adj():
            CG.KG.称重零飘 = tools.ADC_AVG(CG.Pin.kg_adc, CG.KG._校准次数)

    class TEMP:
        # 热电耦参数
        _校准次数 = 10_000
        _采样次数 = 100
        _采样间隔MS = 24
        
        
        热电耦平均温度 = [0, 0]
        k_零飘 = []
        k_max = []
        k_min = []
        满量程read_uv = 994000
        ntc_temp = 0
        热电耦温度 = tools.环形List(60000, (0, 0, 0, time.ticks_ms()))

        # 短路校准
        # -----------------
        # 热电耦合测量的是冷端和探头的温差
        # 为了避免校准时，冷热端温度不一样，可以短路冷端输入信号
        # 然后在校准运放0飘
        # -----------------
        # 当然这也会引入两个问题
        # 1、共模电压改变，不过共模电压主要来自K_REF,影响很小
        # 2、MOS内阻，这是主要问题，可以选择低VGSth，低内阻MOS
        @staticmethod
        async def adj(pga, get_temp):
            CG.TEMP.k_零飘 = []
            CG.TEMP.k_max = []
            CG.TEMP.k_min = []
            CG.Pin.k_sw.value(1)
            await asyncio.sleep(0.3)

            # 遍历 ADC，获取：
            # 零点
            # 最高温度
            # 最低温度
            for k in CG.Pin.k_adc:
                零点 = tools.ADC_AVG(k, CG.TEMP._校准次数)
                CG.TEMP.k_零飘.append(零点)
                CG.TEMP.k_max.append(get_temp((CG.TEMP.满量程read_uv - 零点) / pga))
                CG.TEMP.k_min.append(get_temp(-零点 / pga))

            CG.Pin.k_sw.value(0)

    class POW:
        # pow参数
        _校准次数 = 10_000
        _采样次数 = 100
        _采样间隔MS = 24
        
        
        电流 = tools.环形List(60000, (0, time.ticks_ms()))
        电流零飘 = 0
        输入电压 = tools.环形List(60000, (0, time.ticks_ms()))

        @staticmethod
        def adj():
            CG.POW.电流零飘 = tools.ADC_AVG(
                CG.Pin.pow_adc,
                CG.POW._校准次数,
            )

    class FAN:
        # 风扇参数
        _采样间隔MS = 300
        fan_read = tools.环形List(60000, (0, time.ticks_ms()))

    class WORK:
        # WORK
        work = False
        热压 = False
        热压退出 = False
        _目标温度 = 200
        _目标压力 = 500 * 6
        _焊接目标温度 = 200
        _fan_pwm = 0

    class Pin:
        tft_BLK = 10  # 背光
        tft_RESET = 11  # 复位
        tft_SDO = 12  # SPI miso # 不用必须 None
        tft_SDA = 13  # SPI mosi
        tft_SCK = 14  # SPI sck
        tft_DC = 21  # 数据 - 命令
        tft_CS = 47  # 片选

        # 编码器
        左编码器A = 40
        左编码器B = 41
        左SW = Pin(39, Pin.IN, Pin.PULL_UP)
        右编码器A = 42
        右编码器B = 44
        右SW = Pin(43, Pin.IN, Pin.PULL_UP)

        # 称重
        kg_adc = ADC(8, atten=ADC.ATTN_0DB)

        # 热电耦
        k_ntc = ADC(7, atten=ADC.ATTN_0DB)
        k_sw = Pin(15, Pin.OUT)
        k_adc = []
        for k_i in [6, 4, 5]:
            k_adc.append(ADC(k_i, atten=ADC.ATTN_0DB))

        # 加热片
        pow_pwm = pwm.PWM(48, freq=24000, duty_u16=0)._init(5, 95)
        pow_adc = ADC(2, atten=ADC.ATTN_0DB)

        # H桥
        m_pwm1 = pwm.PWM(16, freq=24_000, duty_u16=65535)._init()
        m_pwm2 = pwm.PWM(17, freq=24_000, duty_u16=65535)._init()
        m_adc = ADC(1, atten=ADC.ATTN_0DB)

        # 风扇pwm
        fan_pwm = pwm.PWM(38, freq=24000, duty_u16=0)._init()
        fan_fead = 18

        # 电压
        v_adc = ADC(9, atten=ADC.ATTN_0DB)

    class UI:
        # UI
        _数据超时MS = 500

        spi: SPI

        st: lcd.LCD

        st波形: lcd.波形
