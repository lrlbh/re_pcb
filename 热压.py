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
    if CG.WORK.热压进入:
        # udp.send("热压进入")-bn
        CG.TEMP.adj()
        CG.H桥.adj()
        CG.KG.adj()
        CG.POW.adj()
        CG.WORK.热压进入 = False

    if CG.WORK.焊接进入:
        # udp.send("焊接进入")
        CG.TEMP.adj()
        CG.POW.adj()
        CG.WORK.焊接进入 = False

    if CG.WORK.热压:
        温控热压()
        压控_open()
    else:
        温控()


async def no_work():
    # 关闭PWM
    CG.Pin.pow_pwm.duty_u16(0)

    # 特殊处理一下热压刚刚关断，电流控制电机复位关断
    if CG.WORK.热压退出:  # 刚刚关断状态
        # udp.send("热压退出")
        CG.H桥.down()  # 电机向下
        await asyncio.sleep(1.2)  # 避免启动电流
        for _ in range(CG.H桥._关闭延迟S):  # 前X秒，如果电流大了也做保护
            if CG.H桥.电流.get_new()[0] >= CG.H桥._保护电流MA:
                break
            await asyncio.sleep(1)
        while 压控_close():  # 电流
            await asyncio.sleep_ms(10)
        CG.WORK.热压退出 = False


def 压控_open():
    if CG.WORK._目标压力 >= CG.KG.kg.get_new()[0]:
        CG.H桥.up()
    else:
        CG.H桥.close()


def 压控_close():
    # 电机大于阈值，说明已经到达目的地了
    if CG.H桥.电流.get_new()[0] >= CG.H桥._关闭电流MA:
        # or CG.H桥.电流.get_new()[0] <= 20:
        CG.H桥.close()
        return False
    else:
        CG.H桥.down()
        return True


def 温控():
    pwm = (CG.WORK._焊接目标温度 - CG.TEMP.热电耦平均温度[0]) * 21
    CG.Pin.pow_pwm.duty_100(pwm)


def 温控热压():
    pwm = (CG.WORK._目标温度 - CG.TEMP.热电耦平均温度[0]) * 100
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
