import time
from lib import st7796便宜, lcd
from llib import tools
from llib.config import CG
from machine import SPI
import asyncio


@tools.catch_and_report("显示屏任务")
async def run():
    CG.UI.spi = SPI(
        1,
        baudrate=100_000_000,
        polarity=0,
        phase=0,
        sck=CG.Pin.tft_SCK,
        mosi=CG.Pin.tft_SDA,
        miso=CG.Pin.tft_SDO,
    )
    CG.UI.st = st7796便宜.ST7796_便宜(
        spi=CG.UI.spi,
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
    st = CG.UI.st
    await st._init_async()

    CG.UI.st波形 = st.new_波形(
        w起点=0,
        h起点=320,  # 波形区域左上角 Y
        size_w=320,
        size_h=160,
        多少格=998,
        # 通道顺序：电压, PWM, 温度, 电流
        波形像素=[10, 10, 10, 10],  # 缩放/像素相关：电压, PWM, 温度, 电流
        data_min=[18, 0, 0, 0],  # 最小值：电压 18，其它 0
        data_max=[
            26,
            100,
            300,
            30,
        ],  # 最大值：电压 26V, PWM 100%, 温度 300℃, 电流 30A
        波形色=[
            st.color_fn(0, 0, 255),  # 电压 → 蓝
            st.color_fn(0, 0, 0),  # PWM  → 黑
            st.color_fn(0, 255, 0),  # 温度 → 绿
            st.color_fn(255, 0, 0),  # 电流 → 红
        ],
        背景色=st.color_fn(255, 255, 255),
    )

    st.def_字符.all += "温度电压流功率校准前后压力风扇转速当前目标热电耦状态热转印热压中焊接加热台℃口范围零飘冷端≈上下限毫伏微最高低自重补偿机保护关断延迟"
    st.load_bmf("/no_delete/字库.bmf", {16: st.def_字符.all, 32: st.def_字符.all})
    st.fill(st.color.黑)
    txt1 = st.new_txt("状态:焊接|1.5/7.8MiB", 32, 背景色=st.color.深灰)
    txt2 = st.new_txt("温度:123/300℃", 32, 背景色=st.color.浅灰)
    txt3 = st.new_txt("冷端:22.22℃", 16, 背景色=st.color.浅灰)
    st.new_txt(
        "UvMax:{:04.0f}mV".format(CG.TEMP.满量程read_uv / 1000),
        16,
        背景色=st.color.浅灰,
    )

    txt5 = st.new_txt("当前温度:111,222,333", 16, 背景色=st.color.浅灰)
    txt6 = st.new_txt("零飘(mV):111,222,333", 16, 背景色=st.color.浅灰)
    txt7 = st.new_txt("最低温度:111,222,333", 16, 背景色=st.color.浅灰)
    txt8 = st.new_txt("最高温度:111,222,333", 16, 背景色=st.color.浅灰)
    txt9 = st.new_txt("POW:99.9A->999%", 32, 背景色=st.color.深灰)
    txt11 = st.new_txt("零飘:999mV", 16, 背景色=st.color.深灰)
    txt12 = st.new_txt("电压:24.4V", 16, 背景色=st.color.深灰)
    txt13 = st.new_txt("压力:9.9/9.9KG", 32, 背景色=st.color.浅灰)
    txt14 = st.new_txt("零飘(mv):999", 16, 背景色=st.color.浅灰)
    txt15 = st.new_txt("自重(g):9999", 16, 背景色=st.color.浅灰)
    txt16 = st.new_txt("电机:9999mA", 32, 背景色=st.color.深灰)
    txt17 = st.new_txt("零飘:999关断:999mA", 16, 背景色=st.color.深灰)
    txt18 = st.new_txt("延迟: 6s保护:999mA", 16, 背景色=st.color.深灰)
    txt19 = st.new_txt("风扇转速:2222 ->999%", 32, 背景色=st.color.浅灰)
    st.new_txt(" " * 20, 32, 背景色=st.color.深灰)
    _ = st.new_txt("电流:0~30 ", 32, 字体色=st.color.红, 背景色=st.color.浅灰)
    _ = st.new_txt("电压:18~26", 32, 字体色=st.color.蓝, 背景色=st.color.浅灰)
    _ = st.new_txt("PWM:0~100 ", 32, 字体色=st.color.黑, 背景色=st.color.浅灰)
    _ = st.new_txt("温度:0~300", 32, 字体色=st.color.绿, 背景色=st.color.浅灰)

    # i = 0
    while True:
        # i+=1
        # s = time.ticks_ms()
        # 是否在工作，工作在什么模式
        if CG.WORK.work:
            字体色 = st.color.黄
        else:
            字体色 = st.color.绿
        if CG.WORK.热压:
            txt1.up_data("热压", 3, 字体色=字体色)
        else:
            txt1.up_data("焊接", 3, 字体色=字体色)

        # 剩余内存，比较耗时
        # if i == 10:
        txt1.up_data(tools.get_mem_str(), 6)
        # i = 0
        # 平均温度
        if (
            time.ticks_diff(time.ticks_ms(), CG.TEMP.热电耦平均温度[1])
            > CG.UI._数据超时MS
        ):
            字体色 = st.color.黄
        elif CG.TEMP.热电耦平均温度[0] > 900:
            字体色 = st.color.红
        else:
            字体色 = st.color.绿

        if CG.WORK.热压:
            temp_t = "{:3.0f}/{:3.0f}℃".format(
                CG.TEMP.热电耦平均温度[0], CG.WORK._目标温度
            )
        else:
            temp_t = "{:3.0f}/{:3.0f}℃".format(
                CG.TEMP.热电耦平均温度[0], CG.WORK._焊接目标温度
            )
        txt2.up_data(
            temp_t,
            3,
            字体色=字体色,
        )

        # 冷端温度
        txt3.up_data("{:5.2f}℃".format(CG.TEMP.ntc_temp), 3)

        # 所有热电耦温度
        txt5.up_data(
            ",".join("{:03.0f}".format(x) for x in CG.TEMP.热电耦温度.get_new()[0:-1]),
            5,
        )

        # 所有热电耦零飘
        txt6.up_data(",".join("{:03.0f}".format(x / 1000) for x in CG.TEMP.k_零飘), 7)

        # 所有热电耦最低温度
        txt7.up_data(
            ",".join("{:03.0f}".format(x + CG.TEMP.ntc_temp) for x in CG.TEMP.k_min), 5
        )

        # 所有热电耦最高温度
        txt8.up_data(
            ",".join("{:03.0f}".format(x + CG.TEMP.ntc_temp) for x in CG.TEMP.k_max), 5
        )

        # 加热电流
        data = list(CG.POW.电流.get_new())
        data[0] = "{:4.1f}A >{:3}%".format(data[0], CG.Pin.pow_pwm.duty_100())
        txt9.up_data_time(data, 4)

        # 加热电流零飘
        txt11.up_data("{:03.0f}".format(CG.POW.电流零飘 / 1000), 3)

        # 输入电压
        txt12.up_data("{:03.1f}".format(CG.POW.输入电压.get_new()[0]), 3)

        # 压力
        data = list(CG.KG.kg.get_new())
        data[0] = "{:3.1f}/{:3.1f}KG".format(data[0] / 1000, CG.WORK._目标压力 / 1000)
        txt13.up_data_time(data, 3)

        # 压力零飘
        txt14.up_data("{:03.0f}".format(CG.KG.称重零飘 / 1000), 7)

        # 压力自重
        txt15.up_data("{:04.0f}".format(CG.KG._自重克), 6)

        # 电机电流
        data = list(CG.H桥.电流.get_new())
        data[0] = "{:4.0f}mA".format(data[0])
        txt16.up_data_time(data, 3)

        # 电机参数
        txt17.up_data("{:03.0f}".format(CG.H桥.零飘 / 1000), 3)
        txt17.up_data("{:03.0f}".format(CG.H桥._关闭电流MA), 9)
        txt18.up_data("{:02.0f}".format(CG.H桥._关闭延迟S), 3)
        txt18.up_data("{:02.0f}".format(CG.H桥._保护电流MA), 9)

        # 风扇
        data = list(CG.FAN.fan_read.get_new())
        data[0] = "{:4.0f}-->{:3.0f}%".format(data[0], CG.Pin.fan_pwm.duty_100())
        txt19.up_data_time(data, 5)

        CG.UI.st波形.更新()

        # udp.send(time.ticks_ms() - s)
        await asyncio.sleep_ms(200)
