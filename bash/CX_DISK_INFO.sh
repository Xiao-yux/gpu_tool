#!/bin/bash

# ==============================================================================
# 网卡信息提取脚本
# 使用方法:
#   ./nic_info.sh                            # 从系统获取实时数据
#   ./nic_info.sh --debug <lspci_vvv_file> <nic_list_file>  # 从文件读取调试数据
# ==============================================================================

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 错误处理函数
error_exit() {
    echo -e "${RED}错误: $1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
用法:
  $(basename "$0")                          # 从系统获取实时数据
  $(basename "$0") --debug <lspci_vvv_file> <nic_list_file>  # 从文件读取调试数据

参数:
  --debug     调试模式，需要两个文件参数
              <lspci_vvv_file>   - lspci -vvv 命令的输出
              <nic_list_file>    - 网卡列表文件（格式: <设备ID>: <描述>）

示例:
  $(basename "$0")
  $(basename "$0") --debug detailed.txt nic_list.txt
EOF
}

# 获取设备前缀（如 a7:00）
get_device_prefix() {
    echo "$1" | awk -F: '{print $1":"$2}'
}

# ==============================================================================
# 1. 参数处理
# ==============================================================================

netinfo(){

debug_mode=false
lspci_vvv_file=""
nic_list_file=""

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
    exit 0
elif [[ "$1" == "--debug" ]]; then
    debug_mode=true
    lspci_vvv_file="$2"
    nic_list_file="$3"

    # 验证文件参数
    if [[ -z "$lspci_vvv_file" ]] || [[ -z "$nic_list_file" ]]; then
        error_exit "调试模式需要两个文件参数"
    fi

    if [[ ! -f "$lspci_vvv_file" ]]; then
        error_exit "lspci -vvv 文件不存在: $lspci_vvv_file"
    fi

    if [[ ! -f "$nic_list_file" ]]; then
        error_exit "网卡列表文件不存在: $nic_list_file"
    fi

    echo -e "${GREEN}调试模式启用${NC}"
    echo "  lspci -vvv 文件: $lspci_vvv_file"
    echo "  网卡列表文件: $nic_list_file"
    echo ""
fi

info(){
echo "======================== 硬盘信息 ========================"
lsblk -d -o NAME,SERIAL,MODEL,TYPE,SIZE,TRAN | grep -v loop

echo "======================== 电源信息 ========================"
dmidecode -t 39 2>/dev/null | awk -F': ' '
BEGIN {count = 1}
/Model Part Number:/ {model = $2}
/Serial Number:/ {serial = $2}
/Max Power Capacity:/ {
    split($2, parts, " ");
    power = parts[1]
}
/^$/ {
    if (model) {
        printf "PSU%d: %s | %s | %s W\n",
               count, model, serial, power
        count++
        model = ""; serial = ""; power = ""
    }
}'
}

# ==============================================================================
# 2. 生成网卡过滤模式列表
# ==============================================================================
echo "正在检测网卡设备..."

declare -a network_patterns
declare -A device_prefixes  # 用于去重

if [[ "$debug_mode" == true ]]; then
    # 从文件读取网卡列表
    mapfile -t network_list < <(cat "$nic_list_file" | sort)
else
    # 从系统实时获取
    mapfile -t network_list < <(lspci -nn 2>/dev/null | grep -iE "ethernet|infiniband|network" | sort)
fi

if [[ ${#network_list[@]} -eq 0 ]]; then
    error_exit "未检测到任何网卡设备"
    info
    exit 1
fi

# 构建模式列表（按设备ID前缀去重）
declare -A unique_nics
for line in "${network_list[@]}"; do
    # 提取设备描述并清理格式
    desc=$(echo "$line" | awk -F': ' '{
        desc = $2
        # 删除 PCI ID [xxxx:xxxx]
        gsub(/ \[[0-9a-f]{4}:[0-9a-f]{4}\]/, "", desc);
        # 删除 rev 信息
        gsub(/ \(rev [0-9a-z]+\)/, "", desc);
        # 合并多个空格
        gsub(/  +/, " ", desc);
        # 删除首尾空格
        gsub(/^[ \t]+|[ \t]+$/, "", desc);
        print desc
    }')

    # 如果描述未出现过，则添加到数组
    if [[ -z "${unique_nics[$desc]}" ]]; then
        unique_nics[$desc]=1
        network_patterns+=("$desc")
    fi
done

# 打印最终结果
echo "发现的网卡型号:"
printf '%s\n' "${network_patterns[@]}"


echo ""
echo -e "${GREEN}开始提取网卡详细信息...${NC}"
echo ""

clean_data() {
    local data="$1"
    # 移除前导和尾随空格
    data=$(echo "$data" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    # 将多个连续空格替换为单个空格
    data=$(echo "$data" | sed 's/[[:space:]]\+/ /g')
    echo "$data"
}


# ==============================================================================
# 3. 解析PCI详细信息
# ==============================================================================

TTY_W=$(stty size|awk '{print $2}')


# 函数：输出设备信息
print_device_info() {
    if [[ -n "$current_device" ]]; then
        # 创建分隔线
        separator=""
        for ((i=0; i<TTY_W; i++)); do
            separator+="-"
        done
        
        # 输出设备信息
        echo "$separator"
        printf "| %-*s |\n" "$((TTY_W-4))" "$current_device"
        printf "| %-*s |\n" "$((TTY_W-2))" "描述: $device_info"
        
        # 格式化输出一行多个信息
        printf "| 部件号(PN): %-20s 序列号(SN): %-20s NUMA节点: %-6s 链路状态: %s  PCI: %s       |\n" "$pn" "$sn" "$numa_node" "$lnksta" "$v0"
        echo "$separator"
        echo ""
    fi
}


if [[ "$debug_mode" == true ]]; then
    pci_input="cat \"$lspci_vvv_file\""
else
    pci_input="lspci -vvv 2>/dev/null"
fi

pci_txt=$(eval "$pci_input")

# 初始化变量
current_device=""
device_prefix=""
device_info=""
in_vpd=0
numa_node=""
pn=""
sn=""
lnksta=""
v0=""
first_output=0

check_network_pattern() {
    local line="$1"
    # echo "检查行: $line"
    line=$(clean_data "$line")
    #echo "check $line"
    for pattern in "${network_patterns[@]}"; do
        # echo "检查模式:$pattern"
        # echo "检查文本:$line"
        # echo "长度文本:${#line}"
        # echo "长度模式:${#pattern}"
        pattern=$(clean_data "$pattern")
        if [[ "$line" == *"$pattern"* ]]; then
            # echo "true"
            return 0  # 匹配成功
        fi
    done
    return 1  # 未匹配
}

while IFS= read -r line; do
    if [[ $line =~ ^[0-9a-f]{2}:[0-9a-f]{2}\.0[[:space:]] ]]; then
        if [[ $in_vpd -eq 1 ]]; then
           print_device_info
        fi
        in_vpd=0
        current_device=$line
        device_info=""
        vendor_id=""
        lnksta=""
        numa_node=""
        pn=""
        sn=""
        v0=""
        in_vpd=0
        #echo "$line"
        if check_network_pattern "$line"; then
            in_vpd=1
           #echo "测试到网卡设备: $line"
        fi 
        
        
        # 重置变量
        
    fi

    if [[ $in_vpd -eq 1 ]]; then
        # echo $line
        if [[ $line == *"Product Name"* ]]; then
            device_info=$(echo "$line" | awk -F': ' '{print $2}')
            device_info=$(clean_data "$device_info")
        fi
        if [[ $line == *"Vendor ID"* ]]; then
            v0=$(echo "$line" | awk '{print $3}')
            v0=$(clean_data "$v0")
           # echo "Vendor ID: $v0"
        fi
        if [[ $line == *"LnkSta:"* ]]; then
            # 提取LnkSta行的内容
            lnksta=$(echo "$line" | awk -F'LnkSta:\t' '{print $2}')
            lnksta=$(clean_data "$lnksta")
          #  echo "链路状态: $lnksta"
        fi
        if [[ $line == *"NUMA node"* ]]; then
            numa_node=$(echo "$line" | awk '{print $3}')
            numa_node=$(clean_data "$numa_node")
          #  echo "NUMA节点: $numa_node"
        fi
        if [[ $line == *"[PN] Part number"* ]]; then
            pn=$(echo "$line" | awk '{print $4}')
            pn=$(clean_data "$pn")
          #  echo "部件号(PN): $pn"
        fi
        if [[ $line == *"[SN] Serial number"* ]]; then 
            sn=$(echo "$line" | awk '{print $4}')
            sn=$(clean_data "$sn")
          #  echo "序列号(SN): $sn"
        fi
        if [[ $line == *"[V0] Vendor specific"* ]]; then
            v0=$(echo "$line" | awk -F '\\[V0\\] Vendor specific:[[:space:]]' '{print $2}')
            v0=$(clean_data "$v0")
        fi
            
        
    fi
done <<< "$pci_txt"
}


diskinfo(){
echo "======================== 硬盘信息 ========================"
lsblk -d -o NAME,SERIAL,MODEL,TYPE,SIZE,TRAN | grep -v loop
}

psuinfo(){
echo "======================== 电源信息 ========================"
dmidecode -t 39 2>/dev/null | awk -F': ' '
BEGIN {count = 1}
/Model Part Number:/ {model = $2}
/Serial Number:/ {serial = $2}
/Max Power Capacity:/ {
    split($2, parts, " ");
    power = parts[1]
}
/^$/ {
    if (model) {
        printf "PSU%d: %s | %s | %s W\n",
               count, model, serial, power
        count++
        model = ""; serial = ""; power = ""
    }
}'
}
if [ "$1" == "--netinfo" ]; then
    netinfo $2
    exit 1
fi

if [ "$1" == "--diskinfo" ]; then
    diskinfo
    exit 1
fi

if [ "$1" == "--psuinfo" ]; then
    psuinfo
    exit 1
fi
main () {
  netinfo
  diskinfo
  psuinfo
}
main