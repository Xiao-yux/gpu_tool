# text_gpu_tool

一个工具菜单

![工具界面](image.png)

## 如何使用

### 1. 安装依赖

```bash
pip install noneprompt toml pyinstaller
```

### 2. 环境配置

1. 安装 DCGM
2. 将其他测试工具放置到以下固定目录：
   - `/home/aisuan/gpu-burn`
   - `/home/aisuan/nccl`
   - `/home/aisuan/fd`

### 3. 打包

```bash
cd old
pyinstaller main.spec
```

---

## 注意事项

- 请确保所有依赖都已正确安装
- 测试工具必须放置在指定的目录中
- 打包前请检查 main.spec 配置文件
```

正在重构中...