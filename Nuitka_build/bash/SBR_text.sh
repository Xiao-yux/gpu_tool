#!/bin/bash
# $1=BDF(例 5a:00.0)  $2=循环次数(默认1000)  $3=delay_ms(默认200)
RP=$1
LOOP=${2:-1000}
DLY=${3:-200}
BUS=$(echo $RP | cut -d: -f1)
DEVFN=$(echo $RP | cut -d: -f2)
DEV=$(echo $DEVFN | cut -d. -f1)
FN=$(echo $DEVFN | cut -d. -f2)

# 计算 Slot Control 地址 = 配置空间 0x18[Cap] + 0x18 内找 Slot Cap 指针
CAP=$(setpci -s $RP CAP_EXP | awk '{print "0x"$1}')
OFF_SLOT_CTRL=$(printf "%d" $((CAP+0x18)) ))

echo "RP=$RP  LOOP=$LOOP  DLY=$DLY ms  SlotCtrl offset=0x$(printf %x $OFF_SLOT_CTRL)"

for ((i=1;i<=LOOP;i++)); do
    # 1. 读当前链路状态
    LNKSTA=$(lspci -vv -s $RP | grep LnkSta:)
    echo "[$i/$LOOP] Before  $LNKSTA"

    # 2. 写 1 触发 SBR
    setpci -s $RP @${OFF_SLOT_CTRL}:w=$(printf %04x 0x0100)   # bit8=1
    sleep 0.01
    # 3. 写 0 释放
    setpci -s $RP @${OFF_SLOT_CTRL}:w=$(printf %04x 0x0000)   # bit8=0
    sleep $(echo "scale=2;$DLY/1000" | bc)

    # 4. 再读链路状态
    LNKSTA_AFTER=$(lspci -vv -s $RP | grep LnkSta:)
    echo "         After   $LNKSTA_AFTER"

    # 5. 简单判 pass/fail
    if ! grep -q "5.0 GT/s\|8.0 GT/s\|16.0 GT/s\|32.0 GT/s" <<<"$LNKSTA_AFTER"; then
        echo "******** FAIL: link down or speed unknown"
        exit 1
    fi
done

echo "=== SBR loop $LOOP finished ==="
# 6. 统计 AER 增量
cat /sys/class/pci_bus/0000:$BUS/device/0000:$RP/aer_dev_correctable
cat /sys/class/pci_bus/0000:$BUS/device/0000:$RP/aer_dev_uncorrectable