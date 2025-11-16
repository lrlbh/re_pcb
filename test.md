# ESP32-S3 芯片 IO 使用安全表格（已配置 VDD_SPI = 3.3V）

| GPIO编号   | 所属电源域  | 默认功能/用途                    | 电压容许范围 | 是否可安全上拉至3.3V | 备注说明 |
|------------|--------------|----------------------------------|----------------|------------------------|-----------|
| GPIO45     | N/A（无 IO） | Strapping 脚位，控制 VDD_SPI     | N/A            | ✅ 可                  | 你已配置 VDD_SPI_FORCE=1，不再受 GPIO45 控制，可浮空或重用 |
| GPIO47     | VDD_SPI      | Octal SPI：SPICLK_P_DIFF         | 3.3V           | ✅ 可                  | 属于 VDD_SPI 电源域，当前已设为 3.3V，可安全连接外部 3.3V 信号 |
| GPIO48     | VDD_SPI      | Octal SPI：SPICLK_N_DIFF         | 3.3V           | ✅ 可                  | 同上 |
| GPIO33~37  | VDD_SPI      | Octal PSRAM 数据线               | 3.3V           | ✅ 可                  | 与 GPIO47/48 同属电压域 |
| GPIO0      | VDD3P3_CPU   | 启动模式控制（Strapping 脚）     | 3.3V           | ✅ 可                  | 默认弱上拉，决定 SPI 启动或下载 |
| GPIO46     | VDD3P3_CPU   | 辅助启动模式控制（Strapping）    | 3.3V           | ⚠️ 避免上拉            | 上拉为未定义状态，可能导致下载模式失效 |
| GPIO3      | VDD3P3_CPU   | 控制 JTAG 类型（Strapping）      | 3.3V           | ⚠️ 谨慎                | 上拉将启用 USB JTAG，占用 GPIO39~42，默认浮空更安全 |
