from machine import Pin,ADC,PWM
from lib import tools

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
        
        
    class 共享数据:
        
        字 = []

        热电耦合温度 = tools.环形List(10000)

        功率片电流 = tools.环形List(10000)
        
        输入电压 = tools.环形List(10000)

        电机电流 = tools.环形List(10000)

        kg = tools.环形List(10000)
        
        fan_read = tools.环形List(10000)

        # 是否进入热压状态
        热压 = False
        
        热压目标温度 = 180
        热压目标压力 = 500 * 10
        
        焊接目标温度 = 0
        
        fan_pwm = 0
        
        
        


    class Pin:
        tft_SCK = Pin(38)  # SPI sck
        tft_SDA = Pin(17)  # SPI mosi
        tft_SDO = None  # SPI miso # 不用必须 None
        tft_RESET = 18  # 复位
        tft_DC = 48  # 数据 - 命令
        tft_CS = 16  # 片选
        tft_BLK = 11  # 背光
        

        # 编码器
        左编码器A =  40
        左编码器B = 39
        左SW = Pin(43, Pin.IN, Pin.PULL_UP)
        右编码器A = 42
        右编码器B = 41
        右SW = Pin(44, Pin.IN, Pin.PULL_UP)

        # 称重
        kg_adc = ADC(5, atten=ADC.ATTN_0DB)

        # 热电耦
        k_ntc = ADC(9, atten=ADC.ATTN_0DB)
        k_sw = Pin(15,Pin.OUT)
        k_adc = []
        for k_i in [6,7,10]:
            k_adc.append(ADC(k_i, atten=ADC.ATTN_0DB))
            

        # 加热片
        pow_pwm = PWM(12, freq=24000,duty_u16=0)
        pow_adc = ADC(1, atten=ADC.ATTN_0DB)


        # H桥
        m_pwm1 = PWM(13, freq=24_000,duty_u16=65535)
        m_pwm2 = PWM(14, freq=24_000,duty_u16=65535)
        m_adc = ADC(2, atten=ADC.ATTN_0DB)
        
        # 风扇pwm
        fan_pwm = PWM(21,freq=24000,duty_u16=0)
        fan_fead = 47
        
        # 电压
        v_adc = ADC(4, atten=ADC.ATTN_0DB) 