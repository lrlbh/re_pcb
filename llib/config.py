from machine import Pin, ADC, SPI
from lib import tools
from lib import pwm, lcd, disk_config, filter
import time
import asyncio


class 方便修改:
    校准次数 = 10_000
    平均次数 = 1
    采样间隔MS = 200


class CG(disk_config.DiskConfig):
    class H桥:
        _校准次数 = 方便修改.校准次数
        _采样次数 = 方便修改.平均次数
        _采样间隔MS = 方便修改.采样间隔MS
        _关闭电流MA = 104
        _保护电流MA = 600
        _关闭延迟S = 4

        零飘 = 0
        电流 = tools.环形List(10000, (0, time.ticks_ms()))

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
        _抖动等待MS = 100

    class KG:
        _校准次数 = 方便修改.校准次数
        _采样次数 = 方便修改.平均次数
        _采样间隔MS = 方便修改.采样间隔MS
        _自重克 = 280
        _PGA = 101
        _传感器量程_g = 500 * 20  # 10KG
        _激励电压mv = 3000

        # 灵敏度uv(满量程输出) / 量程克(10KG=20斤) * 放大倍数
        # 传感器描述里面误差基本来自这里，这里可以使用校准后的参数
        每克电压uv = _激励电压mv / _传感器量程_g * _PGA
        kg = tools.环形List(10000, (0, time.ticks_ms()))
        称重零飘 = 0

        @staticmethod
        def adj():
            CG.KG.称重零飘 = tools.ADC_AVG(CG.Pin.kg_adc, CG.KG._校准次数)

    class TEMP:
        # 热电耦参数
        _校准次数 = 方便修改.校准次数
        _采样次数 = 1
        _采样间隔MS = 5
        _PGA = 80
        _R1阻值 = 430_000
        _输入电压uv = 3_000_000

        热电耦平均温度 = [0, 0]
        # 卡尔曼滤波器 = filter.Kalman(25, Q=4.3e-5, R=1.1)
        卡尔曼滤波器 = filter.Kalman(25, Q=0.000144, R=0.29)
        k_零飘 = []
        k_max = []
        k_min = []
        满量程read_uv = 994000
        ntc_temp = 0
        热电耦温度 = tools.环形List(10000, (0, 0, 0, time.ticks_ms()))

        def get_temp(uv: float) -> float:
            """
            把 Type-K 热电偶的电势（μV, cold-junction 已补偿后的总电势）转换成温度 (°C)
            uv: 电势，单位 microvolts (µV) --- *必须是 µV*
            返回：温度 (°C)。若超出 NIST 多项式定义域，返回 1_000_000 表示错误。
            系数来自 NIST / ITS-90 逆多项式（常见实现与文档一致）。
            """
            # 有效范围（µV）
            if uv < -5891.0 or uv > 54886.0:
                return 1_000_000.0

            # 逆多项式系数（按 NIST/ITS-90，输入 E 单位为 µV，输出为 °C）
            # 区间  : -200 .. 0 °C   对应电势约 -5891 .. 0 µV
            if uv < 0.0:
                c = [
                    0.000000000000e00,
                    2.5949192e-02,
                    -2.1312719e-07,
                    7.9018692e-10,
                    4.2527777e-13,
                    1.3304473e-16,
                    2.0241446e-20,
                    1.2668171e-24,
                    -1.3180580e-29,
                    0.0000000e00,
                ]
            # 区间 : 0 .. 500 °C   对应电势约 0 .. 20644 µV
            elif uv <= 20644.0:
                c = [
                    0.000000000000e00,
                    2.508355e-02,
                    7.860106e-08,
                    -2.503131e-10,
                    8.315270e-14,
                    -1.228034e-17,
                    9.804036e-22,
                    -4.413030e-26,
                    1.057734e-30,
                    -1.052755e-35,
                ]
            # 区间 : 500 .. 1372 °C
            else:
                c = [
                    -1.318058e02,
                    4.830222e-02,
                    -1.646031e-06,
                    5.464731e-11,
                    -9.650715e-16,
                    8.802193e-21,
                    -3.110810e-26,
                ]

            # Horner 求值（从最高次项开始）
            t = c[-1]
            for coef in reversed(c[:-1]):
                t = t * uv + coef
            return t

        # 短路校准
        # -----------------
        # 热电耦合测量的是冷端和探头的温差
        # 为了避免校准时，冷热端温度不一样，可以短路冷端输入信号
        # 然后在校准运放0飘
        # -----------------
        # 当然这也会引入两个问题
        # 1、共模电压改变，不过共模电压主要来自K_REF,影响很小
        # 2、MOS内阻，这是主要问题，可以选择低VGSth，低内阻MOS
        @classmethod
        async def adj(cls):
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
                CG.TEMP.k_max.append(
                    cls.get_temp((CG.TEMP.满量程read_uv - 零点) / cls._PGA)
                )
                # CG.TEMP.k_min.append(get_temp((0 - 零点) / pga))
                CG.TEMP.k_min.append(cls.get_temp(-零点 / cls._PGA))

            CG.Pin.k_sw.value(0)

    class POW:
        # pow参数
        _校准次数 = 方便修改.校准次数
        _采样次数 = 方便修改.平均次数
        _采样间隔MS = 方便修改.采样间隔MS

        电流 = tools.环形List(10000, (0, time.ticks_ms()))
        电流零飘 = 0
        输入电压 = tools.环形List(10000, (0, time.ticks_ms()))

        @staticmethod
        def adj():
            CG.POW.电流零飘 = tools.ADC_AVG(
                CG.Pin.pow_adc,
                CG.POW._校准次数,
            )

    class FAN:
        # 风扇参数
        _采样间隔MS = 1000
        fan_read = tools.环形List(10000, (0, time.ticks_ms()))

    class WORK:
        # WORK
        work = False
        热压 = False
        热压进入 = False
        焊接进入 = False
        热压退出 = False

        _目标温度 = 200
        _目标压力 = 500 * 6
        _焊接目标温度 = 88
        _fan_pwm = 0

    class Pin:
        # ==================== LCD（只改数值，不改名字）================
        tft_BLK = 13  # 新板背光在 IO13（LCD_LED）
        tft_RESET = 14
        tft_SDA = 15
        tft_SCK = 16
        tft_DC = 17
        tft_CS = 18
        tft_SDO = None

        # ==================== 编码器（只改数值，名字完全不动！）================
        左编码器A = 21  # 新板 BMQ_L_A
        左编码器B = 47  # 新板 BMQ_L_B
        左SW = Pin(41, Pin.IN, Pin.PULL_UP)  # 新板 JD（左旋钮按键）

        右编码器A = 44  # 新板 BMQ_R_A
        右编码器B = 43  # 新板 BMQ_R_B
        右SW = Pin(42, Pin.IN, Pin.PULL_UP)  # 新板 JMS（右旋钮按键）

        # ==================== 称重 & 热电偶（完全不变）================
        kg_adc = ADC(7, atten=ADC.ATTN_0DB)
        k_ntc = ADC(4, atten=ADC.ATTN_0DB)
        k_sw = Pin(11, Pin.OUT)

        k_adc = []
        for k_i in [5, 6, 8]:
            k_adc.append(ADC(k_i, atten=ADC.ATTN_0DB))

        # ==================== 加热片（完全不变）================
        pow_pwm = pwm.PWM(12, freq=24000, duty_u16=0)._init(5, 95)
        pow_adc = ADC(10, atten=ADC.ATTN_0DB)

        # ==================== 电机 H 桥（恢复到新板真实引脚）================
        m_pwm1 = pwm.PWM(40, freq=24000, duty_u16=65535)._init()  # 新板 IO40
        m_pwm2 = pwm.PWM(39, freq=24000, duty_u16=65535)._init()  # 新板 IO39
        m_adc = ADC(1, atten=ADC.ATTN_0DB)

        # ==================== 风扇（完全不变）================
        fan_pwm = pwm.PWM(48, freq=24000, duty_u16=0)._init()
        fan_read = 38

        # ==================== 电源电压（完全不变）================
        v_adc = ADC(9, atten=ADC.ATTN_0DB)  # IO09                    # IO09 V_ADC

    class UI:
        # UI
        _数据超时MS = 500

        spi: SPI

        st: lcd.LCD

        st波形: lcd.波形
