import os

import utime


# 获取时间戳字符串
def get_current_time_str():
    # 获取当前时间戳（以秒为单位）
    current_time = utime.time()

    # 将时间戳转换为本地时间元组
    local_time = utime.localtime(current_time)

    # 获取当前时间的毫秒部分
    milliseconds = int((current_time - int(current_time)) * 1000)

    # 格式化日期和时间
    time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
        local_time[0],  # 年
        local_time[1],  # 月
        local_time[2],  # 日
        local_time[3],  # 时
        local_time[4],  # 分
        local_time[5],  # 秒
        milliseconds,  # 毫秒
    )

    return time_str


# 递归创建目录
def ensure_dir_exists(path):
    parts = path.split("/")
    for i in range(1, len(parts) + 1):
        current_path = "/".join(parts[:i])
        try:
            os.mkdir(current_path)
        except OSError as e:
            if e.args[0] != 17:  # 目录已存在
                pass


# 追加内容，附带时间戳
def append_time_line(文件名称, 文本):
    # 分离路径中的目录名和文件名
    directory = "/".join(文件名称.split("/")[:-1])
    ensure_dir_exists(directory)

    # 以追加模式打开文件（'a' 表示追加），如果文件不存在将被创建
    with open(文件名称, "a") as file:
        file.write(get_current_time_str() + "-->" + 文本 + "\n")  # 追加内容并换行
