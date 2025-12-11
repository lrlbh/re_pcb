import time
from machine import ADC
import gc
import asyncio
import sys
import io
from lib import udp  # 你自己的 udp 发送模块


def ADC_AVG(pin_adc: ADC, n):
    uv = 0
    for _ in range(0, n):
        uv += pin_adc.read_uv()
    return uv / n


def ADCS_AVG(pin_adcs, n):
    ret = [0] * len(pin_adcs)
    for _ in range(0, n):
        for i, pin_adc in enumerate(pin_adcs):
            ret[i] += pin_adc.read_uv()

    for i in range(len(ret)):
        ret[i] /= n

    return ret


class 环形List:
    def __init__(self, size, _init_value=0):
        self._buf = [_init_value] * size
        self._size = size
        self._write_idx = 0

    def append(self, value):
        self._buf[self._write_idx] = value
        self._write_idx = (self._write_idx + 1) % self._size

    def append_time(self, value):
        # 可以试试看值修改
        self._buf[self._write_idx] = (value, time.ticks_ms())
        self._write_idx = (self._write_idx + 1) % self._size

    def get_new(self):
        return self._buf[self._write_idx - 1]

    def get_all(self):
        return self._buf[self._write_idx :] + self._buf[: self._write_idx]

    def get_mv():
        pass


def get_mem_str():
    
    # ss = time.ticks_ms()

    # gc.collect()

    
    free = gc.mem_free()
    used = gc.mem_alloc()
    total = free + used

    # 转成 MiB（2^20）
    used_mib = used / (1024 * 1024)
    total_mib = total / (1024 * 1024)

    # 形如：1.2/7.9MiB  → 正好 10 个字符（前提是 <10MiB）
    s = "{:.1f}/{:.1f}MiB".format(used_mib, total_mib)

    # udp.send(time.ticks_ms() - ss)
    # 保证不超过 10 个字符（以后换更大内存板子时也不会溢出）
    return s


def catch_and_report(name: str):
    """
    装饰器用法（推荐写法）：
    @catch_and_report("pow电流采样")
    async def run():
        ...

    或者直接在 main 里包一层也行，见下面两种方式
    """

    def decorator(coro_func):
        async def wrapper(*args, **kwargs):
            try:
                await coro_func(*args, **kwargs)
            except asyncio.CancelledError:
                raise  # 正常取消不报
            except Exception as e:
                buf = io.StringIO()
                sys.print_exception(e, buf)
                error_text = buf.getvalue()

                report = f"【任务死亡】{name}\n{error_text}"
                # print(report)  # 串口看得见
                udp.send(report)  # 网络看得见

                # 可选：写入日志文件
                # try:
                #     from lib import my_file
                #     my_file.append_time_line("/no_delete/任务异常记录.txt", report)
                # except:
                #     pass

                # 任务彻底结束，不再重启

        return wrapper

    return decorator
