# ========= 彻底解决卡死 + QPainter 错误 =========
import matplotlib
matplotlib.use('TkAgg')                 # 彻底杜绝 Qt 冲突
import matplotlib.pyplot as plt
# ============================================

import socket
import threading
from datetime import datetime
from collections import Counter
import numpy as np
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================== 众数滤波器 ==================
class 众数滤波器:
    def __init__(self, n=101):
        self._data = [None] * n
    def read(self, data):
        self._data.pop(0)
        self._data.append(data)
        valid = [x for x in self._data if x is not None]
        if not valid:
            return data
        return Counter(valid).most_common(1)[0][0]

# ================== 卡尔曼滤波器 ==================
class 卡尔曼滤波器:
    def __init__(self, init_value=85.0, Q=0.0005, R=0.8):
        """
        Q: 过程噪声（调小→更平滑，调大→更跟随原始数据）
        两次测量最大变化速度: (相邻两次合理最大温差)² × 0.2~0.5
        
        R: 测量噪声（调小→更信测量，调大→更信预测）
        传感器噪声: 稳定段标准差² × 3~5倍   
        """
        self.x = init_value    # 估计值
        self.P = 1.0           # 估计误差协方差
        self.Q = Q             # 过程噪声
        self.R = R             # 测量噪声

    def update(self, z):
        # 预测
        P_pred = self.P + self.Q
        
        # 更新
        K = P_pred / (P_pred + self.R)      # 卡尔曼增益
        self.x = self.x + K * (z - self.x)  # 更新估计值
        self.P = (1 - K) * P_pred          # 更新误差协方差
        
        return self.x

# ================== 配置 ==================
UDP_IP = "0.0.0.0"
UDP_PORT = 1111
MAX_POINTS = 300

# 全局数据
times = []
raw_temps = []
mode_temps = []
kalman_temps = []

# 实例化滤波器
mode_filter = 众数滤波器(n=101)
kalman_filter = 卡尔曼滤波器(init_value=25.0,Q=4.3e-5 , R=1.1)

# ================== 绘图设置 ==================
plt.ion()
fig, ax = plt.subplots(figsize=(12, 6.5))
raw_line,    = ax.plot([], [], '#cccccc', linewidth=1,   label='原始温度')
mode_line,   = ax.plot([], [], 'red',      linewidth=2.5, label='众数滤波 101点')
kalman_line, = ax.plot([], [], 'blue',     linewidth=2.5, label='卡尔曼滤波（推荐）')

ax.set_xlabel('运行时间 (秒)')
ax.set_ylabel('温度 (°C)')
ax.set_title('热压机实时温度监控\n原始 vs 众数滤波 vs 卡尔曼滤波（最近1000点）', 
             fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.4)
ax.legend(loc='upper left')


# 预分配坐标数组，避免频繁创建
plot_x = np.zeros(MAX_POINTS)
plot_raw = np.zeros(MAX_POINTS)
plot_mode = np.zeros(MAX_POINTS)
plot_kalman = np.zeros(MAX_POINTS)

# 用来控制刷新频率
last_draw_time = 0.0
REFRESH_INTERVAL = 0.1   # 每 100ms 强制刷新一次（人眼无感，彻底解决延迟）

def update_plot():
    if not times:
        return
    
    current_len = len(times)
    
    # 只更新前 current_len 个点（关键！避免每次复制整个列表）
    plot_x[:current_len] = times
    plot_raw[:current_len] = raw_temps
    plot_mode[:current_len] = mode_temps
    plot_kalman[:current_len] = kalman_temps
    
    # 关键优化1：只每 5 个点才真正重绘一次（50Hz → 10Hz刷新，人眼无感）
    global last_draw_time
    now = datetime.now().timestamp()
    
    if now - last_draw_time >= REFRESH_INTERVAL:
        # 每 100ms 才真正重绘一次
        raw_line.set_data(plot_x[:current_len], plot_raw[:current_len])
        mode_line.set_data(plot_x[:current_len], plot_mode[:current_len])
        kalman_line.set_data(plot_x[:current_len], plot_kalman[:current_len])
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        last_draw_time = now

# ================== UDP 服务 ==================
# 在函数外面加一个计数器
print_counter = 0

def udp_server():
    global times, raw_temps, mode_temps, kalman_temps, start_time, print_counter
    start_time = None
    print_counter = 0   # 初始化
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("热压机温度监控已启动（每100个新点打印一次标准差）")

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            text = data.decode('utf-8', errors='ignore').strip()
            if ',' not in text:
                continue
                
            temp_str, ts_str = text.split(",", 1)
            temp = float(temp_str)
            timestamp = float(ts_str) / 1000

            if start_time is None:
                start_time = datetime.now()
                print(f"单片机已连接 → {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

            times.append(timestamp)
            raw_temps.append(temp)
            mode_temps.append(mode_filter.read(temp))
            kalman_temps.append(kalman_filter.update(temp))

            # 保留最近 MAX_POINTS 个点
            if len(times) > MAX_POINTS:
                times = times[-MAX_POINTS:]
                raw_temps = raw_temps[-MAX_POINTS:]
                mode_temps = mode_temps[-MAX_POINTS:]
                kalman_temps = kalman_temps[-MAX_POINTS:]

            update_plot()

            # 关键修复：只在新增点时计数
            print_counter += 1
            if print_counter % 100 == 0:
                std_raw    = np.std(raw_temps)
                std_mode   = np.std(mode_temps)
                std_kalman = np.std(kalman_temps)
                print(f"\n【第 {print_counter} 个新点】当前窗口标准差（最近 {len(raw_temps)} 点）:")
                print(f"   原始温度  → 标准差 = {std_raw:.4f} °C")
                print(f"   众数滤波  → 标准差 = {std_mode:.4f} °C")
                print(f"   卡尔曼滤波 → 标准差 = {std_kalman:.4f} °C  ← 推荐关注")
                print(f"   卡尔曼衰减倍数 ≈ {std_raw / std_kalman:.1f} 倍\n")

        except Exception as e:
            print("出错（已忽略）:", e)
            
threading.Thread(target=udp_server, daemon=True).start()
print("窗口已打开，准备接收数据……")
print("提示：蓝色卡尔曼曲线最丝滑，推荐重点看它！")
plt.show(block=True)