import time
from machine import Pin
import asyncio
from lib import udp, tools
from lib.旋转编码器 import Encoder
from llib.config import CG


def 右按钮任务():
    上次触发时间 = time.ticks_ms()

    def t(pin):
        nonlocal 上次触发时间
        本次触发时间 = time.ticks_ms()
        if time.ticks_diff(本次触发时间, 上次触发时间) < CG.BMQ._抖动等待MS:
            return

        ###############code###############
        # 是否工作
        CG.WORK.work = not CG.WORK.work

        if CG.WORK.work:  # 进入工作分支
            if CG.WORK.热压:
                CG.WORK.热压进入 = True
                CG.WORK.热压首次足压力 = False
            else:
                CG.WORK.焊接进入 = True
        else:  # 退出工作分支
            if CG.WORK.热压:  # 热压退出需要复位升降台
                CG.WORK.热压退出 = True
        ###############code###############

        上次触发时间 = 本次触发时间

    return t


# CG.Pin.pow_pwm.duty_100(50)
def 左按钮任务():
    上次触发时间 = time.ticks_ms()

    def t(pin):
        nonlocal 上次触发时间
        本次触发时间 = time.ticks_ms()
        # 切换任务模式
        if time.ticks_diff(本次触发时间, 上次触发时间) < CG.BMQ._抖动等待MS:
            return

        ###############code###############
        if CG.WORK.work:
            return
        CG.WORK.热压 = not CG.WORK.热压
        ###############code###############
        上次触发时间 = 本次触发时间

    return t


def 编码器右(变化量, *args):
    if CG.WORK.热压:
        CG.WORK._热压目标温度 += 变化量
    else:
        CG.WORK._焊接目标温度 += 变化量


def 编码器左(变化量, *args):
    if CG.WORK.热压:
        CG.WORK._热压自动关闭时间 += 变化量
    else:
        CG.WORK._fan_pwm += 变化量 * 6550
        if CG.WORK._fan_pwm < 0:
            CG.WORK._fan_pwm = 0
        elif CG.WORK._fan_pwm > 65535:
            CG.WORK._fan_pwm = 65535


# 主循环，保持程序运行
@tools.catch_and_report("编码器任务")
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

    # 上升沿，松开触发
    CG.Pin.右SW.irq(trigger=Pin.IRQ_RISING, handler=右按钮任务())
    CG.Pin.左SW.irq(trigger=Pin.IRQ_RISING, handler=左按钮任务())

    while True:
        await asyncio.sleep(100)
