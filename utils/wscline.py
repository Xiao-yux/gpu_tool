import asyncio
import threading
from typing import Dict, Any

import websockets
from websockets.protocol import State  # 15.x 版本
import json,aiofiles
import time
from utils.tool import Tools

class Cline:
    def __init__(self, wsurl: str,log):
        self.wsurl = wsurl
        self.ws = None
        self.log = log
        self.loop = None
        self.thread = None
        self._running = False
        self._send_task = None
        self._lock = threading.Lock()
        self.status = {}
        self.Tools = Tools()

    def start(self):
        """启动后台任务"""
        if self._running:
            return
        self._running = True
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
        self.log.msg("[Cline] 后台任务已启动")

    def _run_async_loop(self):
        """在新线程中运行事件循环"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connection_manager())
        finally:
            self.loop.close()

    async def _connection_manager(self):
        """连接管理器"""
        while self._running:
            await asyncio.sleep(2)
            try:
                async with websockets.connect(self.wsurl) as ws:
                    self.ws = ws
                    self.log.msg(f"[Cline] 已连接到服务器")
                    self.log.msg(f"[Cline] {self.ws.response}")
                    # 启动定时发送任务
                    self._send_task = asyncio.create_task(self._send_loop())
                    # 接收消息循环
                    try:
                        async for message in ws:
                            await self._handle_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        pass
                    finally:
                        self._send_task.cancel()
                        try:
                            await self._send_task
                        except asyncio.CancelledError:
                            pass

            except websockets.exceptions.ConnectionClosed:
                self.log.msg("[Cline] 连接断开")
            except Exception as e:
                self.log.msg(f"[Cline] 错误: {e}")
            finally:
                self.ws = None
                self.log.msg("关闭链接")

            if self._running:
                await asyncio.sleep(5)

    async def _send_loop(self):
        """每10秒发送一次"""
        while self._running:
            try:
                await asyncio.sleep(10)
                # 检查状态：websockets 15.x 使用 State.OPEN
                if self.ws and self.ws.state == State.OPEN:

                    await self.ws.send("{'info':'ping','msg':'在线维持'}")
                else:
                    break
            except Exception as e:
                self.log.msg(f"[Cline] 发送错误: {e}")
                break

    async def _send_sys_info(self):
        """发送系统配置信息"""
        status = await self._gather_sys_info()
        with self._lock:
            self.status = status

        # 15.x 中使用 state 检查或直接发送
        await self.ws.send(json.dumps(status, ensure_ascii=False))
        self.log.msg(f"[Cline] 数据已发送: {status.get('time')}")

    async def _gather_sys_info(self):
        """收集系统信息"""
        loop = asyncio.get_event_loop()

        # 并发执行命令
        results = await asyncio.gather(
            loop.run_in_executor(None, self.Tools.run_command, 'cat /proc/cpuinfo'),
            loop.run_in_executor(None, self.Tools.get_sys_info, '--meminfo'),
            loop.run_in_executor(None, self.Tools.run_command,
                                 "lsblk -d -o NAME,SERIAL,MODEL,TYPE,SIZE,TRAN | grep -v loop"),
            loop.run_in_executor(None, self.Tools.get_eth_info, '--netinfo'),
            loop.run_in_executor(None, self.Tools.get_eth_info, '--psuinfo'),
            loop.run_in_executor(None, self.Tools.get_gpu_info),
            loop.run_in_executor(None, self.Tools.run_command, "ip -br addr"),
            loop.run_in_executor(None, self.Tools.run_command, "date"),
            loop.run_in_executor(None, self.Tools.get_serial_number)
        )

        return {
            "ip": results[6],
            "SN": results[8],
            "time": results[7],
            "cpuinfo": results[0],
            "meminfo": results[1],
            "diskinfo": results[2],
            "netinfo": results[3],
            "psuinfo": results[4],
            "gpuinfo": results[5]
        }

    async def _handle_message(self, message: str):
        """处理服务器消息"""
        self.log.msg(f"[Cline] 收到: {message}")
        try:
            # 1. 只解析一次，别再覆盖同名变量
            msg_dict = json.loads(message)

            if msg_dict.get('info') == 'cmd':
                cmd = msg_dict.get('cmd')

                if cmd == 'sysinfo':
                    status = await self._gather_sys_info()
                    await self.ws.send(json.dumps(status, ensure_ascii=False))

                elif cmd == 'ttyget':
                    # 2. 确保类里定义了 ttyget 协程方法
                    info = await self.ttyget()
                    await self.ws.send(json.dumps(info, ensure_ascii=False))

            elif msg_dict.get('info') == 'log':
                self.log.msg(f"[Cline] 收到: {msg_dict.get('msg')}")

        except Exception as e:
            import traceback, sys
            self.log.msg("hand错误: " + str(e))
            self.log.msg("traceback:\n" + traceback.format_exc())  # ← 关键


    async def ttyget(self):
        TTY_DEV = "/dev/tty4"  # 按实际改
        BAUD = 115200
        try:
            # aiofiles 支持异步 read
            async with aiofiles.open(TTY_DEV, "rb", buffering=0) as tty:
                # 简单设置 115200 8N1（ioctl 需要额外库，这里跳过）
                data = await tty.read(4096)
            return {"tty": TTY_DEV, "data": data.decode(errors="ignore")}
        except Exception as exc:
            return {"tty": TTY_DEV, "error": str(exc)}



    def is_connected(self):
        """检查连接状态"""
        return self.ws is not None and self.ws.state == State.OPEN

    def stop(self):
        """停止任务"""
        self._running = False
        if self.thread:
            self.thread.join(timeout=5)