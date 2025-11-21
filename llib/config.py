from machine import Pin, ADC, SPI
from llib import tools
from lib import pwm, st7796便宜, lcd
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
        KG采样间隔MS = 24

        # 热电耦参数
        K采样校准次数 = 10_000
        K采样次数 = 100
        K采样间隔MS = 24

        # H桥参数
        H桥采样校准次数 = 10_000
        H桥样次数 = 100
        H桥样间隔MS = 24

        # pow参数
        POW采样校准次数 = 10_000
        POW采样次数 = 100
        POW采样间隔MS = 24

        # 风扇参数
        风扇采样间隔 = 300

    def m_下():
        CG.Pin.m_pwm1.duty_u16(0)
        CG.Pin.m_pwm2.duty_u16(65535)

    def m_上():
        CG.Pin.m_pwm1.duty_u16(65535)
        CG.Pin.m_pwm2.duty_u16(0)

    def m_close():
        CG.Pin.m_pwm1.duty_u16(65535)
        CG.Pin.m_pwm2.duty_u16(65535)

    class K:
        pass

    class mem:
        热电耦平均温度 = [0, 0]
        k_零飘 = []
        k_max = []
        k_min = []
        满量程read_uv = 994000
        ntc_temp = 0

        热电耦温度 = tools.环形List(60000, (0, 0, 0, time.ticks_ms()))

        电流 = tools.环形List(60000, (0, time.ticks_ms()))
        电流零飘 = 0

        输入电压 = tools.环形List(60000, (0, time.ticks_ms()))

        电机电流 = tools.环形List(60000, (0, time.ticks_ms()))

        kg = tools.环形List(60000, (0, time.ticks_ms()))

        fan_read = tools.环形List(60000, (0, time.ticks_ms()))

        # 是否进入工作状态
        work = False

        热压 = False

        热压退出 = False

        热压目标温度 = 120
        热压目标压力 = 500 * 6

        焊接目标温度 = 0

        fan_pwm = 0

        称重零飘 = 0

        电机零飘 = 0

    class disk:
        数据超时ms = 500
        自重克 = 280
        热压电机关闭电流ma = 144
        电机保护电流 = 600
        电机关闭延迟 = 6

    class adj:
        async def 热电耦(pga, get_temp):
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

        def 加热电流():
            CG.mem.电流零飘 = tools.ADC_AVG(
                CG.Pin.pow_adc,
                CG.频率.POW采样校准次数,
            )

        def 称重():
            CG.mem.称重零飘 = tools.ADC_AVG(CG.Pin.kg_adc, CG.频率.KG校准次数)

        def 电机():
            CG.mem.电机零飘 = tools.ADC_AVG(CG.Pin.m_adc, CG.频率.H桥采样校准次数)

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


class temp_data:
    spi = SPI(
        1,
        baudrate=100_000_000,
        polarity=0,
        phase=0,
        sck=CG.Pin.tft_SCK,
        mosi=CG.Pin.tft_SDA,
        miso=CG.Pin.tft_SDO,
    )

    # st = st7796便宜.ST7796_便宜(
    st = st7796便宜.ST7796_便宜(
        spi=spi,
        dc=CG.Pin.tft_DC,
        size=lcd.LCD.Size.st7796,
        bl=CG.Pin.tft_BLK,
        rst=CG.Pin.tft_RESET,
        cs=CG.Pin.tft_CS,
        旋转=1,
        color_bit=24,
        像素缺失=(0, 0, 0, 0),
        逆CS=False,
    )

    st波形 = st.new_波形(
        w起点=0,  
        h起点=320,  # 波形区域左上角 Y
        size_w=320,  
        size_h=160,  
        多少格=998,
        # 通道顺序：电压, PWM, 温度, 电流
        波形像素=[10, 10, 10, 10],  # 缩放/像素相关：电压, PWM, 温度, 电流
        data_min=[18, 0, 0, 0],  # 最小值：电压 18，其它 0
        data_max=[26, 100, 300, 30],  # 最大值：电压 26V, PWM 100%, 温度 300℃, 电流 30A
        波形色=[
            st.color_fn(0, 0, 255),  # 电压 → 蓝
            st.color_fn(0, 0, 0),  # PWM  → 黑
            st.color_fn(0, 255, 0),  # 温度 → 绿
            st.color_fn(255, 0, 0),  # 电流 → 红
        ],
        背景色=st.color_fn(255, 255, 255),
    )
