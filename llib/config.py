from machine import Pin, ADC, PWM
from llib import tools
import time
import asyncio


class CG:
    class 频率:
        # 编码器参数
        BMQ轮询间隔MS = 50
        BMQ抖动等待MS = 10

        # 称重参数
        KG校准次数 = 10_000
        KG采样次数 = 100
        KG采样间隔MS = 100

        # 热电耦参数
        K采样校准次数 = 10_000
        K采样次数 = 100
        K采样间隔MS = 100

        # H桥参数
        H桥采样校准次数 = 10_000
        H桥样次数 = 100
        H桥样间隔MS = 100

        # pow参数
        POW采样校准次数 = 10_000
        POW采样次数 = 100
        POW采样间隔MS = 100

        # 风扇参数
        风扇采样间隔 = 1000

    def m_上():
        CG.Pin.m_pwm1.duty_u16(0)
        CG.Pin.m_pwm2.duty_u16(65535)

    def m_下():
        CG.Pin.m_pwm1.duty_u16(65535)
        CG.Pin.m_pwm2.duty_u16(0)

    def m_close():
        CG.Pin.m_pwm1.duty_u16(65535)
        CG.Pin.m_pwm2.duty_u16(65535)

    class K:
        pass

    class mem:
        字 = []

        热电耦平均温度 = [0,0]
        k_零飘 = []
        k_max = []
        k_min = []
        满量程read_uv = 994000
        ntc_temp = 0

        async def adj_热电耦(pga, get_temp):
            CG.mem.k_零飘 = []
            CG.mem.k_max = []
            CG.mem.k_min = []
            CG.Pin.k_sw.value(1)
            await asyncio.sleep(0.3)

            # 遍历 ADC，获取：
            # 零点
            # 最高温度
            # 最低温度
            for k in CG.Pin.k_adc:
                零点 = tools.ADC_AVG(k, CG.频率.K采样校准次数)
                CG.mem.k_零飘.append(零点)
                CG.mem.k_max.append(get_temp((CG.mem.满量程read_uv - 零点) / pga))
                CG.mem.k_min.append(get_temp(-零点 / pga))

            CG.Pin.k_sw.value(0)

        热电耦温度 = tools.环形List(20000, (0, 0, 0, time.ticks_ms()))

        功率片电流 = tools.环形List(20000, (0, time.ticks_ms()))

        输入电压 = tools.环形List(20000, (0, time.ticks_ms()))

        电机电流 = tools.环形List(20000, (0, time.ticks_ms()))

        kg = tools.环形List(20000, (0, time.ticks_ms()))

        fan_read = tools.环形List(20000, (0, time.ticks_ms()))

        # 是否进入工作状态
        work = False

        热压 = False

        热压退出 = False

        热压目标温度 = 120
        热压目标压力 = 500 * 6
        热压电机关闭电流ma = 40

        焊接目标温度 = 0

        fan_pwm = 0

    class disk:
        数据超时ms = 500

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
        pow_pwm = PWM(48, freq=24000, duty_u16=0)
        pow_adc = ADC(2, atten=ADC.ATTN_0DB)

        # H桥
        m_pwm1 = PWM(16, freq=24_000, duty_u16=65535)
        m_pwm2 = PWM(17, freq=24_000, duty_u16=65535)
        m_adc = ADC(1, atten=ADC.ATTN_0DB)

        # 风扇pwm
        fan_pwm = PWM(38, freq=24000, duty_u16=0)
        fan_fead = 18

        # 电压
        v_adc = ADC(9, atten=ADC.ATTN_0DB)
