from llib import tools
from llib.config import CG
import asyncio
from lib import udp
import sys
import io

async def run():
    try :
        while True:
            if CG.mem.work:
                await work()
            else:
                await no_work()

            await asyncio.sleep_ms(300)
    except Exception as e:
        # 捕获完整异常信息（含文件名、行号）
        buf = io.StringIO()
        sys.print_exception(e, buf)
        text = buf.getvalue()
        udp.send("=== 异常捕获 ===")
        udp.send(text)



async def work():
    温控()
    if CG.mem.热压:
        压控_open()
        
    udp.send(
        f"温度: {CG.mem.热电耦温度.get_new()[0]:.2f}\t"
        f"kg: {CG.mem.kg.get_new()[0]:.0f}\t"
        f"加热电流: {CG.mem.功率片电流.get_new()[0]:.2f}\t"
        f"电机电流: {CG.mem.电机电流.get_new()[0]:.2f}\t"
        f"目标压力: {CG.mem.热压目标压力}"
        f"目标温度: {CG.mem.热压目标温度}"
        # f"加热PWM: {pwm}"
    )


async def no_work():
    CG.Pin.pow_pwm.duty_u16(0)
    if CG.mem.热压退出:
        CG.mem.热压退出 = False
        CG.m_下()
        # 这里延迟也应该保护电流过大情况
        # 避免升降台损坏
        await asyncio.sleep(9) 
        while 压控_close():
            await asyncio.sleep_ms(100)


def 压控_open():
    if CG.mem.热压目标压力 >= CG.mem.kg.get_new()[0]:
        CG.m_上()
    else:
        CG.m_close()


def 压控_close():
    
    udp.send(
        f"温度: {CG.mem.热电耦温度.get_new()[0]:.2f}\t"
        f"kg: {CG.mem.kg.get_new()[0]:.0f}\t"
        f"加热电流: {CG.mem.功率片电流.get_new()[0]:.2f}\t"
        f"电机电流: {CG.mem.电机电流.get_new()[0]:.2f}\t"
        f"风扇转速: {CG.mem.fan_read.get_new()[0]:.2f}\t"
        f"风扇PWM: {CG.mem.fan_pwm:.2f}\t"
        f"加热PWM: 0"
    )
     
    if (  # 电机已经到达目的地
        CG.mem.热压电机关闭电流ma <= CG.mem.电机电流.get_new()[0]
        or CG.mem.电机电流.get_new()[0] <= 20  # 已经到达过目的地了
    ):
        CG.m_close()
        return False
    else:
        CG.m_下()
        return True


def 温控():
    pwm = (CG.mem.热压目标温度 - CG.mem.热电耦温度.get_new()[0]) * 655
    pwm = int(pwm)
    if pwm > 65535:
        pwm = 65535
    elif pwm < 0:
        pwm = 0
    CG.Pin.pow_pwm.duty_u16(pwm)
