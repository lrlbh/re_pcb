from machine import Pin
import asyncio
from lib.旋转编码器 import Encoder
from llib.config import CG


def 右按钮任务():
    # 是否工作
    CG.WORK.work = not CG.WORK.work

    if CG.WORK.work:  # 开始工作
        if CG.WORK.热压:
            CG.WORK.热压进入 = True
        else:
            CG.WORK.焊接进入 = True
    else:  # 退出工作
        if CG.WORK.热压:  # 热压退出需要复位升降台
            CG.WORK.热压退出 = True


def 左按钮任务():
    # 切换任务模式
    if CG.WORK.work:
        return
    CG.WORK.热压 = not CG.WORK.热压


def 编码器右(变化量, *args):
    if CG.WORK.热压:
        CG.WORK._目标温度 += 变化量
    else:
        CG.WORK._焊接目标温度 += 变化量


def 编码器左(变化量, *args):
    if CG.WORK.热压:
        CG.WORK._目标压力 += 变化量 * 100
    else:
        CG.WORK._fan_pwm += 变化量 * 6550
        if CG.WORK._fan_pwm < 0:
            CG.WORK._fan_pwm = 0
        elif CG.WORK._fan_pwm > 65535:
            CG.WORK._fan_pwm = 65535


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
                await asyncio.sleep_ms(CG.BMQ._抖动等待MS)
                if CG.Pin.左SW.value():
                    break
            左按钮任务()

        if not CG.Pin.右SW.value():
            while True:
                await asyncio.sleep_ms(CG.BMQ._抖动等待MS)
                if CG.Pin.右SW.value():
                    break
            右按钮任务()

        await asyncio.sleep_ms(CG.BMQ._抖动等待MS)
