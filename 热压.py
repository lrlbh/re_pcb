import time
from lib import tools
from llib.config import CG
import asyncio


@tools.catch_and_report("热压任务")
async def run():
    while True:
        if CG.WORK.work:
            await work()
        else:
            await no_work()

        await asyncio.sleep_ms(50)


async def work():
    # 校准
    if CG.WORK.热压进入:
        CG.TEMP.adj()
        CG.H桥.adj()
        CG.KG.adj()
        CG.POW.adj()
        CG.WORK.热压进入 = False

    if CG.WORK.焊接进入:
        CG.TEMP.adj()
        CG.POW.adj()
        CG.WORK.焊接进入 = False

    if CG.WORK.热压:
        温控热压()
        压控_open()
    else:
        温控焊接()


async def no_work():
    # 关闭PWM
    CG.Pin.pow_pwm.duty_u16(0)

    # 特殊处理一下热压刚刚关断，电流控制电机复位关断
    if CG.WORK.热压退出:  # 刚刚关断状态
        if CG.WORK.热压首次足压力:
            CG.H桥.down()  # 电机向下
            await asyncio.sleep(0.1)  # 避免启动电流
            for _ in range(CG.H桥._关闭延迟S * 5):  # 前X秒，如果电流大了也做保护
                if CG.H桥.电流.get_new()[0] >= CG.H桥._保护电流MA:
                    CG.H桥.close()
                    CG.WORK.热压退出 = False
                    return
                await asyncio.sleep(0.2)
        while 压控_close():  # 电流
            await asyncio.sleep_ms(10)
        CG.WORK.热压退出 = False


def 自动关闭():
    if (
        time.ticks_diff(time.ticks_ms(), CG.WORK.热压进入ms)
        >= CG.WORK._热压自动关闭时间 * 1000
    ):
        CG.WORK.热压退出 = True
        CG.WORK.work = not CG.WORK.work


def 压控_open():
    # 还没有达到目标温度，不上升
    if not (
        CG.WORK._热压目标温度 - CG.TEMP.热电耦平均温度[0] <= CG.WORK._热压自动上升温差
    ):
        return

    # 第一次足压力后，不在允许上升，防止连接杠崩飞情况下，损坏升降台
    if CG.WORK.热压首次足压力:
        自动关闭()
        return

    if CG.WORK._目标压力 >= CG.KG.kg.get_new()[0]:
        CG.H桥.up()
    else:
        CG.H桥.close()
        CG.WORK.热压进入ms = time.ticks_ms()
        CG.WORK.热压首次足压力 = True


def 压控_close():
    # 电机大于阈值，说明已经到达目的地了
    if CG.H桥.电流.get_new()[0] >= CG.H桥._关闭电流MA:
        # or CG.H桥.电流.get_new()[0] <= 20:
        CG.H桥.close()
        return False
    else:
        CG.H桥.down()
        return True


def 温控焊接():
    pwm = (CG.WORK._焊接目标温度 - CG.TEMP.热电耦平均温度[0]) * 21
    CG.Pin.pow_pwm.duty_100(pwm)


def 温控热压():
    pwm = (CG.WORK._热压目标温度 - CG.TEMP.热电耦平均温度[0]) * 21
    CG.Pin.pow_pwm.duty_100(pwm)


# udp.send(
#     f"温度: {CG.mem.热电耦温度.get_new()[0]:.2f}\t"
#     f"kg: {CG.mem.kg.get_new()[0]:.0f}\t"
#     f"加热电流: {CG.mem.电流.get_new()[0]:.2f}\t"
#     f"电机电流: {CG.mem.电机电流.get_new()[0]:.2f}\t"
#     f"风扇转速: {CG.mem.fan_read.get_new()[0]:.2f}\t"
#     f"风扇PWM: {CG.mem.fan_pwm:.2f}\t"
#     f"加热PWM: 0"
# )
