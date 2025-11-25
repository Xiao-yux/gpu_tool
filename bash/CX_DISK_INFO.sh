#!/usr/bin/env bash
# mlx_sn.sh  —— 自动列出所有 Mellanox ConnectX 网卡 SN
echo "============ 网卡信息 ============"
lspci -nn 2>/dev/null | grep -iE "ethernet|infiniband|network" | sort | awk -F': ' '{
    split($1, parts, " ");
    device_id = parts[1];

    if (!seen[device_id]++) {
        desc = $2
        gsub(/ \[[0-9a-f]{4}:[0-9a-f]{4}\]/, "", desc);
        gsub(/ \(rev ..\)/, "", desc);
        gsub(/  +/, " ", desc);
        print device_id ": " desc
    }
}'
echo "----------------Mellanox 设备SN-------------------------"

printf "%-12s %-45s %10s %s\n" "pci" "Name" "SN"
for d in /sys/bus/pci/devices/*; do
    # 判断是不是 Mellanox 设备（15b3 是 Mellanox 的 Vendor ID）
    [[ "$(cat "$d/vendor" 2>/dev/null)" == "0x15b3" ]] || continue

    pci=${d##*/}
    model=$(lspci -s "$pci" 2>/dev/null | cut -d: -f3- | xargs)
    sn=$(cat "$d/vpd" 2>/dev/null | strings | awk 'p{print $1;exit} /SN|sn/{p=1}')
    [[ -z "$sn" ]] && sn="N/A"
    #统计数量网卡数量
    
    printf "%-12s %-45s %10s %s\n" "$pci" "$model" "$sn"

done

printf "\n"
echo "============ 硬盘信息 ============"
lsblk -d -o NAME,SERIAL,MODEL,TYPE,SIZE,TRAN | grep -v loop



echo "===== 电源信息 ====="
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

if [[ $count -eq 1 ]]; then
    echo "未检测到电源信息"
fi
echo