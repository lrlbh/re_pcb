from lib import udp

class 环形内存:
    __slots__ = ("buf", "mv", "cap", "head", "tail", "count", "_empty")

    # size == 宽 * 高 * 单像素字节
    # 只为存储像素设置，所以不必当心单次append超出环形结构
    def __init__(self, size_w: int, size_h: int,size_byte: int,
                 多少格: int, max: list,波形色:list, 背景色:bytes):
        self.波形色 = 波形色
        self.背景色 = 背景色
        self.size_h = size_h
        self.size_byte = size_byte
        self.size = int(size_w * size_h * size_byte)
        self.buf = bytearray(self.size)
        self.mv = memoryview(self.buf)
        self.当前下标 = 0      # 最旧字节位置
        self.多少格 = 多少格
        self.max = max

    def append_data(self, data: list) -> None:
        td =  bytearray( len(self.背景色)* self.size_h) 
        
        
        
        for i in range(len(data)):
            index = data[i] / self.max[i] * self.size_h
            index = int(index)
            if index >= self.size_h :
                index = self.size_h-1
            if index < 0:
                index = 0
            td[index*3:index*3+3] = self.波形色[i]
        
        # if len(td)>len(self.背景色)* self.size_h:
        #     return
        # 交给你现有的 append（保持不改）
        self.append(td)
 
    # 单次追加数据越多越慢
    # 波形显示一般宽大于高,直接用这个
    def append(self, data: bytes) -> None:
        if self.当前下标 == self.size :
            self.当前下标 =0
        
        for i in range(len(data)):
            self.buf[self.当前下标+i] = data[i]
            
        self.当前下标 = self.当前下标+len(data)
        # udp.send(self.当前下标 )

    # bytearray中 末尾数据越多越慢
    # 万一性能不够，整合两个函数为一个        
    def append_mv(self, data: bytes) -> None:
        if self.当前下标 == self.size :
            self.当前下标 =0
        下一次下标 = self.当前下标+len(data)
        self.buf[self.当前下标:下一次下标] = data
        self.当前下标 = 下一次下标

    def get_all_data(self):
        return self.mv[self.当前下标:self.size],self.mv[0:self.当前下标]
    
    
    
# def test():
#     from time import ticks_ms, ticks_diff    
#     每列多少像素 =  b'a' * 3 * 200   # 高
#     波形区域多少列 =  50    # 宽
#     测试次数 =    2
    
#     t = 环形内存(波形区域多少列 * len(每列多少像素))
    
#     append耗时 = 0
#     get_all_data耗时 = 0

#     for i in range(测试次数):
#         for i in range(波形区域多少列):
#             t0 = ticks_ms()
#             t.append_mv(每列多少像素)  # 每次追加 940 字节数据
#             append耗时 += ticks_diff(ticks_ms(), t0)
#             t0 = ticks_ms()
#             _ = t.get_all_data()
#             get_all_data耗时 += ticks_diff(ticks_ms(), t0)
#         print(f"append_mv数据量、测试测数、耗时ms:{
#             len(每列多少像素),波形区域多少列,append耗时}")
#         append耗时 = 0

#     for i in range(测试次数):
#         for i in range(波形区域多少列):
#             t0 = ticks_ms()
#             t.append(每列多少像素)  # 每次追加 940 字节数据
#             append耗时 += ticks_diff(ticks_ms(), t0)
#             t0 = ticks_ms()
#             _ = t.get_all_data()
#             get_all_data耗时 += ticks_diff(ticks_ms(), t0)
#         print(f"append数据量、测试测数、耗时ms:{
#             len(每列多少像素),波形区域多少列,append耗时}")
#         append耗时 = 0


  
# if __name__ == "__main__":
#     test()
