from lib import st7796便宜, udp, lcd
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
    # st._init()
    st.fill(st.color.蓝)
    st.txt("阿斯顿", 0, 0, 32)

    while True:
        await asyncio.sleep(1)
        continue
        # st.fill(st.color.亮彩.柠黄)
        st._set_window(0, 0, 319, 99)
        # st._write_data_bytes(st.color.亮彩.天蓝*320 *100)
        t1, t2 = CG.共享数据.t.get_all_data()
        st._write_data_bytes(t1)
        st._write_data_bytes(t2)
        await asyncio.sleep(1)
    st.def_字符.all += "阿斯顿正弦波示例真·左移滚动（整块重绘）"
    st.load_bmf(
        "/no_delete/霞鹜_Regular_等宽--阈值114--2500常用+ascii--16_24_32_40_48_56_64_72.bmf"
    )

    # st.load_bmf("/no_delete/字体.bmf",None)
    # st.show_bmp("/no_delete/pexels-chris-czermak-1280625-2444403.bmp")
    # st.txt("电阿斯顿压:18.4241234",0,0,32,st.color.基础灰阶.白,st.color.基础灰阶.黑,True)

    # ====== 1) 静态文字 ======
    # ===== 1) 静态文字（不动） =====
    # 假设将文字显示在 (0, 0)，高度大约 32 像素
    text = "123456789ABCDEFGHIJK"  # 初始内容，右侧留空格避免抖动
    y = 0
    x = 0
    CHAR_H = 32

    import time

    while True:
        # 1) 清空这一行显示区域
        # st._set_window(x, y, st._width-1, y + CHAR_H - 1)
        # blank = bytearray([0,0,0] * st._width)  # RGB888纯黑背景
        # for _ in range(CHAR_H):
        #     st._write_data_bytes(blank)

        # 2) 显示当前字符串（一次性绘制整行字符）
        st.txt(text, x, y, CHAR_H, st.color.基础灰阶.白, st.color.基础灰阶.黑, True)

        # 3) 模拟滚动 —— 字符真左移，新字符补到末尾
        # new_char = "#"   # 你可以换成实时数据
        # text = text[1:] + new_char
        udp.send()
        time.sleep(1)  # 控制速度
