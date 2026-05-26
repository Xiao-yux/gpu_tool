"""配置文件"""
import os
import sys
import toml
import shutil

__global_config = None

def get_config() -> "dict":
    """获取全局配置单例"""
    global __global_config
    if __global_config is None:
        __global_config = Config().config
    return __global_config


class Config:
    """配置文件管理类"""
    def __init__(self):
        self.tmp_config = None
        self.config = {}
        self.init()
        
    def get_config_path(self) -> str:
        """获取默认配置文件路径（项目根目录下的 config.toml）"""
        # 获取当前文件 (core/config.py) 所在的目录 (core/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上一级目录，到达项目根目录
        project_root = os.path.dirname(current_dir)
        # 拼接配置文件路径
        return os.path.join(project_root, "config.toml")

    def _deep_update(self, old_dict: dict, new_dict: dict):
        """
        深度合并字典：以 new_dict 为基准，将 old_dict 中已有的值覆盖进去。
        效果：保留旧值，添加新键值对。
        """
        for key, value in old_dict.items():
            if key in new_dict:
                # 如果新旧都是字典，递归合并，保证嵌套配置也能正确更新
                if isinstance(value, dict) and isinstance(new_dict[key], dict):
                    self._deep_update(value, new_dict[key])
                else:
                    # 旧配置中存在且不是字典，用旧值覆盖新值（保留用户设置）
                    new_dict[key] = value
            else:
                # 旧配置中存在但新配置中没有的键，直接加入（视需求而定，通常保留旧版特有配置）
                new_dict[key] = value

    def init(self):
        max_retries = 5
        retry_count = 0
        
        try:
            # 1. 加载临时配置 (作为新版本配置的基准)
            self.tmp_config = toml.load(self.get_config_path())
            path1 = self.tmp_config["PATH"]["config_file"]
            
            # 2. 检查目标配置文件是否存在
            if os.path.exists(path1):
                self.config = toml.load(path1)
                
                # ====== 新增逻辑：版本对比与配置合并 ======
                new_version = self.tmp_config.get('version')
                old_version = self.config.get('version')
                
                # 版本号不一致时进行合并 (确保两者都有 version 字段且不相等)
                if new_version and old_version and new_version != old_version:
                    print(f"检测到配置版本更新: {old_version} -> {new_version}，正在合并配置...")
                    
                    # 以新配置为底板
                    merged_config = self.tmp_config.copy()
                    
                    # 将旧配置的值深度合并进去
                    self._deep_update(self.config, merged_config)
                    
                    # 更新版本号为新版本
                    merged_config['version'] = new_version
                    
                    # 将合并后的配置写回文件
                    try:
                        with open(path1, 'w', encoding='utf-8') as f:
                            toml.dump(merged_config, f)
                            
                        # 更新内存中的 config
                        self.config = merged_config
                        print("配置合并完成并已保存。")
                    except IOError as e:
                        print(f"写入合并配置文件失败: {e}")
                        raise
                # ==========================================

            else:
                # 3. 使用 while 循环进行重试 (文件不存在时的逻辑)
                while retry_count < max_retries:
                    try:
                        # 确保目标目录存在
                        parent_dir = os.path.dirname(path1)
                        if parent_dir and not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, exist_ok=True)
                            
                        # 尝试复制文件
                        shutil.copy(self.get_config_path(), path1)
                        
                        # 复制成功后加载配置，并跳出循环
                        self.config = toml.load(path1)
                        break 
                        
                    except IOError as e:
                        retry_count += 1
                        print(f"复制配置文件失败 (尝试 {retry_count}/{max_retries}): {e}")
                        
                # 如果重试次数耗尽仍然失败
                if retry_count >= max_retries:
                    raise FileNotFoundError(f"无法复制配置文件到 {path1}，已达最大重试次数")
                    
        except KeyError as e:
            print(f"配置文件格式错误，缺少必要的键: {e}")
            raise
        except FileNotFoundError as e:
            print(f"找不到必要的文件: {e}")
            raise
        except Exception as e:
            print(f"加载配置文件时发生未知错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
