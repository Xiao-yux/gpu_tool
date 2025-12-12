# text_gpu_tool

一个工具菜单
### 1. 安装依赖 & 克隆仓库

```bash
git clone https://github.com/Xiao-yux/gpu_tool.git
cd gpu_tool
apt install -y gcc g++ clang lld make patchelf python3-dev ccache python3
pip install noneprompt toml Nuitka tqdm
make 
```
编译完成的可执行文件在 `dist` 目录下

### 2. 环境配置

1. 运行一遍程序，然后编辑 `/etc/gpu_tool/config.toml` 文件，填写工具路径 \
```toml
# 需要配置的项目
[PATH]
config_file= "/etc/gpu_tool/config.toml" #配置文件  此项需要在编译前配置好
#其他项也可以在编译前配置，会成为默认配置文件，无需每次更新后修改
fd_path = "/home/path/fd"  #fieldiag路径
gpu_burn_path = "/home/path/gpu-burn"  #gpu_burn路径
nccl_path = "/home/path/nccl-tests/build"  #nccl测试路径
fd_exe = "fieldiag.sh"  #fieldiag可执行文件
gpu_burn_exe = "gpu_burn"  #gpu_burn可执行文件
nccl_exe = "all_reduce_perf"  #nccl可执行文件

[LOG]
log_path = "/home/path/log"  #日志路径
log_file = "gpu_tool_debug.log"  #日志文件
```


### 3菜单项
    阅读 ./readme.doc 文件

## 有问题请提issue
欢迎提出更多服务器测试项目

