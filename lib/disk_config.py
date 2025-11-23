import json
import os
import asyncio


class DiskConfig:
    @classmethod
    def to_dict(cls):
        data = {}
        # 遍历当前类（包括 CG 和它的所有子类）的所有属性
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                continue

            attr = getattr(cls, attr_name)

            # 关键：判断是不是我们定义的配置子类（H桥、KG、TEMP 等）
            if isinstance(attr, type):  # 是类
                # 检查这个类有没有需要保存的配置（有 _ 开头的属性）
                sub_config = {}
                for sub_attr in dir(attr):
                    if sub_attr.startswith("_") and not sub_attr.startswith("__"):
                        value = getattr(attr, sub_attr)
                        if not callable(value):
                            try:
                                json.dumps(value)  # 测试能否序列化
                                sub_config[sub_attr] = value
                            except Exception:
                                pass
                if sub_config:
                    data[attr_name] = sub_config
        return data

    @classmethod
    def from_dict(cls, data: dict):
        for key, value in data.items():
            if not isinstance(value, dict):
                continue
            # 找到对应的子类
            sub_cls = getattr(cls, key, None)
            if sub_cls and isinstance(sub_cls, type):
                for k, v in value.items():
                    if k.startswith("_") and hasattr(sub_cls, k):
                        setattr(sub_cls, k, v)

    @classmethod
    async def auto_save_async(cls, path, interval=2.0):
        # 目录不存在创建
        def ensure_dir(p):
            dir_path = "/".join(p.split("/")[:-1])
            if not dir_path:
                return
            parts = [part for part in dir_path.split("/") if part]
            current = ""
            for part in parts:
                current += "/" + part
                try:
                    os.mkdir(current)
                except OSError as e:
                    if e.args[0] != 17:  # EEXIST
                        raise

        # 确保目录存在
        ensure_dir(path)
        last_data = None

        # 加载配置
        try:
            with open(path, "r") as f:
                raw = f.read().strip()
                if raw:
                    loaded = json.loads(raw)
                    cls.from_dict(loaded)
                    last_data = cls.to_dict()
                    # print(f"[Config] 加载成功: {path}")
                else:
                    raise ValueError("empty")
        except Exception:
            # print(f"[Config] 加载失败({e})，使用默认值")
            last_data = cls.to_dict()
            with open(path, "w") as f:
                json.dump(last_data, f)

        # 循环监控变更
        while True:
            await asyncio.sleep(interval)
            # s = time.ticks_ms()
            current = cls.to_dict()
            if current == last_data:
                continue
            try:
                with open(path, "w") as f:
                    json.dump(current, f)
                last_data = current
                # print(f"[Config] 已保存 → {path}")
            except Exception:
                pass
                # print(f"[Config] 保存失败: {e}")
            # print(time.ticks_ms() - s)



