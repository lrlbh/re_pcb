import time
from lib import st7796便宜, udp, lcd
from llib import tools
from llib.config import CG
from machine import SPI, Pin
import asyncio


def 电压_POW电流_当前PWM():
    pass


def 电机电流_目标压力_当前压力():
    pass


def K温度_NTC温度():
    pass


def 风扇转速_PWM():
    pass


async def run():
    # while True:
    #     await asyncio.sleep(3)
    spi = SPI(
        1,
        baudrate=10_000_000,
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
    await st._init_async()
    st.def_字符.all += "温度电压流功率校准前后压力风扇转速当前目标热电耦状态热转印热压中焊接加热台℃口范围零飘冷端≈"
    st.load_bmf("/no_delete/字库.bmf")
    st.fill(st.color.深灰)

    st.txt("状态:", 0, 0, 32, 缓存=False, 背景色=st.color.浅灰)
    st.txt("热电耦:", 0, 32, 32, 缓存=False, 背景色=st.color.深灰)
    st.txt("冷端:", 224, 32, 16, 缓存=False, 背景色=st.color.深灰)
    st.txt("UvMax:", 224, 48, 16, 缓存=False, 背景色=st.color.深灰)
    st.txt(
        "{0:4.0f}mV".format(CG.mem.满量程read_uv / 1000),
        272,
        48,
        16,
        缓存=False,
        背景色=st.color.深灰,
    )
    st.txt("校准:", 0, 64, 16, 缓存=False, 背景色=st.color.浅灰)
    st.txt("k1:", 0, 80, 16, 缓存=False, 背景色=st.color.深灰)
    st.txt("k2:", 116, 80, 16, 缓存=False, 背景色=st.color.深灰)
    st.txt("k3:", 232, 80, 16, 缓存=False, 背景色=st.color.深灰)

    while True:
        # 工作模式
        if CG.mem.热压:
            st.txt("转印|", 80, 0, 32, 缓存=True, 背景色=st.color.浅灰)
        else:
            st.txt("焊接|", 80, 0, 32, 缓存=True, 背景色=st.color.浅灰)

        # 当前剩余内存
        st.txt(
            tools.get_mem_str(),
            160,
            0,
            32,
            缓存=True,
            背景色=st.color.浅灰,
        )

        # 热电偶温度，绿正常，黄超时，红3个热电偶都断线了
        cl = st.color.绿
        if (
            time.ticks_diff(time.ticks_ms(), CG.mem.热电耦平均温度[1])
            > CG.disk.数据超时ms
        ):
            cl = st.color.黄
        elif CG.mem.热电耦平均温度[0] > 900:
            cl = st.color.红
        st.txt(
            "{:5.1f}℃".format(CG.mem.热电耦平均温度[0]),
            112,
            32,
            32,
            字体色=cl,
            缓存=True,
            背景色=st.color.深灰,
        )

        # 冷端温度
        st.txt(
            "{:5.2f}℃".format(CG.mem.ntc_temp),
            264,
            32,
            16,
            缓存=True,
            背景色=st.color.深灰,
        )

        # 热电偶校准参数
        w = 40
        for i in range(3):
            txt = (
                "{:3.0f} ".format(CG.mem.k_min[i] + CG.mem.ntc_temp)
                + "{:3.0f} ".format(CG.mem.k_零飘[i] / 1000)
                + "{:3.0f}|".format(CG.mem.k_max[i] + CG.mem.ntc_temp)
            )
            st.txt(txt, w, 64, 16, 缓存=True, 背景色=st.color.浅灰)
            w += 96

        # 每路热电偶温度
        w = 24
        for i in range(3):
            txt = "{:06.2f}℃ ".format(CG.mem.热电耦温度.get_new()[i])
            st.txt(
                txt,
                w,
                80,
                16,
                缓存=True,
                背景色=st.color.深灰,
            )
            w += 116

        # st.txt(str(CG.mem_data.热电耦平均温度),112,32,32,缓存=True)
        # st.txt(str(CG.mem.热电耦温度.get_new()[0]), 112, 32, 32, 缓存=True)
        # st.txt(str(CG.mem.热电耦温度.get_new()[1]), 112, 64, 32, 缓存=True)
        # st.txt(str(CG.mem.热电耦温度.get_new()[2]), 112, 96, 32, 缓存=True)
        # st.txt(str(CG.mem.热电耦平均温度), 112, 128, 32, 缓存=True)
        # for 温度 in  CG.mem_data.热电耦合温度:
        #     pass
        await asyncio.sleep(0.2)
