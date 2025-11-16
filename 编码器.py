from machine import Pin
import asyncio
from lib.旋转编码器 import Encoder
from llib.config import CG
from lib import udp



def 左按钮任务():
    # udp.send("左按下")
    # CG.Pin.m_pwm2.duty_u16(65535)
    # CG.Pin.m_pwm1.duty_u16(65535)    
    
    if CG.Pin.m_pwm2.duty_u16() >= 20000:
        CG.Pin.m_pwm1.duty_u16(65535)   
        CG.Pin.m_pwm2.duty_u16(0)
    else:
        CG.Pin.m_pwm1.duty_u16(0)   
        CG.Pin.m_pwm2.duty_u16(65535)
        
    
def 编码器左(变化量, *args):
    # udp.send(f"左当前值: {变化量} ")
    CG.共享数据.热压目标压力 += 变化量 *10
    CG.共享数据.fan_pwm += 变化量 * 6550
    if CG.共享数据.fan_pwm > 65535:
        CG.共享数据.fan_pwm = 65535
    if CG.共享数据.fan_pwm < 0:
        CG.共享数据.fan_pwm = 0
    

def 右按钮任务():
    CG.共享数据.热压 = not  CG.共享数据.热压
    
    udp.send("右按下")
    # if CG.Pin.m_pwm2.duty_u16() >= 20000:
    #     CG.Pin.m_pwm1.duty_u16(65535)   
    #     CG.Pin.m_pwm2.duty_u16(0)
    # else:
    #     CG.Pin.m_pwm1.duty_u16(0)   
    #     CG.Pin.m_pwm2.duty_u16(65535)
        
    # CG.共享数据.热压 = not CG.共享数据.热压
    # if not data.热压:
    #     pin.m_pwm2.duty_u16(0)
    #     pin.m_pwm1.duty_u16(65535)        

def 编码器右(变化量, *args):
    CG.共享数据.热压目标温度 += 变化量
    # udp.send(f"右当前值: {变化量} ")



# 主循环，保持程序运行
async def run():
    
    Encoder(
    pin_x=Pin(CG.Pin.左编码器A, Pin.IN, Pin.PULL_UP),  # 编码器X相引脚
    pin_y=Pin(CG.Pin.左编码器B, Pin.IN, Pin.PULL_UP),  # 编码器Y相引脚
    v=0,  # 初始值
    div=4,  # 分辨率倍数
    # vmin=0,  # 最小值限制
    # vmax=30,  # 最大值限制
    callback=lambda _, change, *args: 编码器左(change, *args))

    Encoder(
        pin_x=Pin(CG.Pin.右编码器A, Pin.IN, Pin.PULL_UP),  # 编码器X相引脚
        pin_y=Pin(CG.Pin.右编码器B, Pin.IN, Pin.PULL_UP),  # 编码器Y相引脚
        v=0,  # 初始值
        div=4,  # 分辨率倍数
        # vmin=0,  # 最小值限制
        # vmax=30,  # 最大值限制
        callback=lambda _, change, *args: 编码器右(change, *args))

    
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
        
        

        




