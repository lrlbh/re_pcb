import ntptime  # 946684800
from lib import my_file, udp  # type: ignore
# import main1
# ntptime.settime()   # 同步时钟

import time
import uasyncio
from machine import WDT, reset, SPI, Pin  # type: ignore
import H桥

import 编码器
import 显示屏
import 热电偶
import pow电流采样
import 称重
import 热压
import 风扇
from llib.config import CG


# wdt = WDT(id=0, timeout=15_000)


# from machine import PWM
# PWM(12, freq=25_000).duty_u16(20000)
# CG.共享数据.t.append_data([0,0,0])
async def main():
    tasks = {
        "称重": uasyncio.create_task(称重.run()),
        "显示屏": uasyncio.create_task(显示屏.run()),
        "热电偶": uasyncio.create_task(热电偶.run()),
        "pow电流采样": uasyncio.create_task(pow电流采样.run()),
        "H桥": uasyncio.create_task(H桥.run()),
        "热压": uasyncio.create_task(热压.run()),
        "风扇": uasyncio.create_task(风扇.run()),
        "编码器任务": uasyncio.create_task(编码器.run()),
        # "配置文件任务": uasyncio.create_task(
        #     CG.auto_save_async("/no_delete/config.json", 1)
        # ),
    }
    
    
    # 如果没有意外定时喂狗
    while True:
        # # 意外，任务死亡
        for name, task in tasks.items():
            # noinspection PyUnresolvedReferences
            if task.done():
                udp.send(f"任务-{name}-死亡!")
                my_file.append_time_line(
                    "/no_delete/任务死亡记录.txt", f"任务-{name}-死亡!"
                )
                # 重启设备 
                # reset()

        # wdt.feed()
        await uasyncio.sleep(6)


uasyncio.run(main())
