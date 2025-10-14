# text_gpu_tool

一个工具菜单

![工具界面](img/memu.png)
![cpu](img/cpu.jpg)
![gpu](img/gpu.jpg)
![disk](img/disk.jpg)
## 如何使用



### 1. 安装依赖 & 克隆仓库

```bash
git clone https://github.com/Xiao-yux/text_gpu_tool.git
cd Nuitka_build
apt install -y gcc g++ clang lld make patchelf python3-dev ccache python3
pip install noneprompt toml Nuitka
make 
```
编译完成的可执行文件在 `dist` 目录下

### 2. 环境配置

1. 安装 nvidia驱动 ,cuda
2. 安装 dcgmi
3. 运行一遍程序，然后编辑 `/etc/aisuan/config.toml` 文件，填写相关信息


### 其他
我编译了ubuntu2204带cjktty补丁的内核，放在linux-kernel目录下
一个代证书签名一个不带

## 有问题请提issue
欢迎提出更多服务器测试项目

#待更新
!(box.md)