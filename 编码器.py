from machine import Pin
import asyncio
from lib.旋转编码器 import Encoder
from llib.config import CG
from lib import udp


def 右按钮任务():
    CG.mem_data.work = not CG.mem_data.work
    if CG.mem_data.热压:
        CG.mem_data.热压退出 = True


def 左按钮任务():
    if CG.mem_data.work:
        return
    CG.mem_data.热压 = not CG.mem_data.热压

    udp.send("右按下")


def 编码器右(变化量, *args):
    CG.mem_data.热压目标温度 += 变化量


def 编码器左(变化量, *args):
    if CG.mem_data.热压:
        CG.mem_data.热压目标压力 += 变化量 * 10
    else:
        CG.mem_data.fan_pwm += 变化量 * 6550


# 主循环，保持程序运行
async def run():
    Encoder(
        pin_x=Pin(CG.Pin.左编码器A, Pin.IN, Pin.PULL_UP),  # 编码器X相引脚
        pin_y=Pin(CG.Pin.左编码器B, Pin.IN, Pin.PULL_UP),  # 编码器Y相引脚
        v=0,  # 初始值
        div=4,  # 分辨率倍数
        # vmin=0,  # 最小值限制
        # vmax=30,  # 最大值限制
        callback=lambda _, change, *args: 编码器左(change, *args),
    )

    Encoder(
        pin_x=Pin(CG.Pin.右编码器A, Pin.IN, Pin.PULL_UP),  # 编码器X相引脚
        pin_y=Pin(CG.Pin.右编码器B, Pin.IN, Pin.PULL_UP),  # 编码器Y相引脚
        v=0,  # 初始值
        div=4,  # 分辨率倍数
        # vmin=0,  # 最小值限制
        # vmax=30,  # 最大值限制
        callback=lambda _, change, *args: 编码器右(change, *args),
    )

    while True:
        if not CG.Pin.左SW.value():
            while True:
                await asyncio.sleep_ms(CG.频率.BMQ抖动等待MS)
                if CG.Pin.左SW.value():
                    break
            左按钮任务()

        if not CG.Pin.右SW.value():
            while True:
                await asyncio.sleep_ms(CG.频率.BMQ抖动等待MS)
                if CG.Pin.右SW.value():
                    break
            右按钮任务()

        await asyncio.sleep_ms(CG.频率.BMQ轮询间隔MS)
