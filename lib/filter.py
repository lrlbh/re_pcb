class Kalman:
    def __init__(self, init_value=25.0, Q=0.0005, R=0.8):
        """
        Q: 过程噪声（调小→更平滑，调大→更跟随原始数据）
        两次测量最大变化速度: (相邻两次合理最大温差)² × 0.2~0.5

        R: 测量噪声（调小→更信测量，调大→更信预测）
        传感器噪声: 稳定段标准差² × 3~5倍
        """
        self.x = init_value  # 估计值
        self.P = 1.0  # 估计误差协方差
        self.Q = Q  # 过程噪声
        self.R = R  # 测量噪声

    def get_data(self, data):
        # 预测
        P_pred = self.P + self.Q

        # 更新
        K = P_pred / (P_pred + self.R)  # 卡尔曼增益
        self.x = self.x + K * (data - self.x)  # 更新估计值
        self.P = (1 - K) * P_pred  # 更新误差协方差

        return self.x
