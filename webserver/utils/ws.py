import inspect
import os
import json
from telnetlib import AYT

import websockets
import asyncio

from websockets.server import ServerConnection
from utils.db import Clineinfo


class WebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()  # 存储所有连接的客户端
        self.client_info = {}  # 存储客户端信息，key为websocket对象，value为客户端信息字典
        self.loop = None  # 事件循环引用
        self.app = None  # Flask应用上下文引用

    def set_event_loop(self, loop):
        """设置事件循环引用，用于同步调用异步方法"""
        self.loop = loop
    
    def set_app(self, app):
        """设置Flask应用上下文引用"""
        self.app = app

    async def handle_client(self, websocket: ServerConnection) -> None:
        path = websocket.request.path  # 想要 URI 从这里拿  # pyright: ignore[reportAttributeAccessIssue]
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"  # pyright: ignore[reportAttributeAccessIssue]
        self.clients.add(websocket)
        client_id = str(id(websocket))
        # 初始化客户端信息
        self.client_info[websocket] = {
            "id": client_id,
            "ip": client_ip,
            "SN": "",
            "time": "",
            "cpuinfo": "",
            "meminfo": "",
            "diskinfo": "",
            "netinfo": "",
            "psuinfo": "",
            "gpuinfo": ""
        }
        # 广播客户端列表更新
        await self.broadcast_client_list()
        
        # 自动请求系统信息
        sysinfo_request = json.dumps({
            "info": "cmd",
            "cmd": "sysinfo"
        })
        await self.send_to_client(websocket, sysinfo_request)
        try:
            async for msg in websocket:  # pyright: ignore[reportGeneralTypeIssues]
                print(f"收到消息: {msg}")
                print(f"当前连接的客户端数量: {len(self.clients)}")
                # 解析客户端消息
                try:
                    data = json.loads(msg)
                    if isinstance(data, dict):
                        # 处理来自web客户端的请求
                        if data.get("type") == "get_info":
                            # 查找目标客户端
                            target_client_id = data.get("client_id")
                            
                            # 首先尝试从数据库获取客户端信息
                            client_sn = None
                            for client in self.clients:
                                if self.client_info[client]["id"] == target_client_id:
                                    client_sn = self.client_info[client].get("SN")
                                    break
                            
                            if client_sn and self.app:
                                with self.app.app_context():
                                    cached_info = Clineinfo.get_by_sn(client_sn)
                                    if cached_info:
                                        # 从数据库获取到缓存信息，直接返回
                                        await self.send_to_client(websocket, json.dumps({
                                            "type": "client_info",
                                            "client_id": target_client_id,
                                            "info": cached_info.to_dict(),
                                            "from_cache": True
                                        }))
                                        return
                            
                            # 数据库中没有缓存，向目标客户端发送sysinfo请求
                            for client in self.clients:
                                if self.client_info[client]["id"] == target_client_id:
                                    sysinfo_request = json.dumps({
                                        "info": "cmd",
                                        "cmd": "sysinfo"
                                    })
                                    await self.send_to_client(client, sysinfo_request)
                                    break
                        else:
                            # 更新客户端信息
                            self.client_info[websocket].update(data)
                            
                            # 如果包含SN信息，则更新到数据库
                            if "SN" in data and data["SN"] and self.app:
                                # 添加id到数据中
                                data["id"] = self.client_info[websocket]["id"]
                                # 更新或创建数据库记录
                                with self.app.app_context():
                                    Clineinfo.update_or_create(data)
                            
                            # 广播更新后的客户端信息
                            await self.broadcast_client_info(websocket)
                except json.JSONDecodeError:
                    pass
        except websockets.ConnectionClosed:
            pass
        finally:
            print(f"客户端断开连接: {client_ip}")
            self.clients.discard(websocket)
            if websocket in self.client_info:
                del self.client_info[websocket]
            # 广播客户端列表更新
            await self.broadcast_client_list()


    def run_cmd(self,msg):
        return os.popen(msg).read()

    def get_client_list(self):
        """同步方法：获取客户端列表"""
        clients_list = []
        for client in self.clients:
            if client in self.client_info:
                clients_list.append({
                    "id": self.client_info[client]["id"],
                    "ip": self.client_info[client]["ip"],
                    "sn": self.client_info[client].get("SN", ""),
                    "online": True
                })
        return clients_list

    def get_client_info(self, client_id):
        """同步方法：获取指定客户端的详细信息"""
        for client in self.clients:
            if client in self.client_info and self.client_info[client]["id"] == client_id:
                return self.client_info[client]
        return None

    async def request_client_info(self, client_id):
        """异步方法：向指定客户端请求系统信息"""
        for client in self.clients:
            if client in self.client_info and self.client_info[client]["id"] == client_id:
                sysinfo_request = json.dumps({
                    "info": "cmd",
                    "cmd": "sysinfo"
                })
                await self.send_to_client(client, sysinfo_request)
                return True
        return False

    async def get_status(self):
        """客户端会返回
            {
        "SN": "",
        "bmcip":"",
        "cpuinfo": "",
        "diskinfo": "",
        "gpuinfo": ",
        "ip": "",
        "meminfo": "",
        "netinfo": "",
        "psuinfo": "",
        "manufacturer": "",
        "pn": "",
        "time": "2026年 01月 30日 星期五 12:05:47 CST\n"
            }  -> json
        """
        a= {
            "info": "cmd",
            "cmd": "sysinfo"
        }
        await self.send(a)
    
    async def send(self, message):
        """向所有连接的客户端发送消息"""
        if not self.clients:
            print("没有客户端连接，无法发送消息")
            return
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.ConnectionClosed:
                disconnected_clients.add(client)
        # 清理已断开的客户端
        
        print(f"清除:{disconnected_clients}")
        self.clients -= disconnected_clients

    async def send_ip(self, ip, message):
        """向指定IP的客户端发送消息"""
        for client in self.clients:
            if self.client_info[client]["ip"] == ip:
                return await self.send_to_client(client, message)

    async def broadcast_client_list(self):
        """广播客户端列表到所有连接的客户端"""
        clients_list = []
        for client in self.clients:
            if client in self.client_info:
                clients_list.append({
                    "id": self.client_info[client]["id"],
                    "ip": self.client_info[client]["ip"],
                    "online": True
                })
        
        message = json.dumps({
            "type": "client_list",
            "clients": clients_list
        })
        await self.send(message)

    async def broadcast_client_info(self, websocket):
        """广播指定客户端的信息"""
        if websocket in self.client_info:
            message = json.dumps({
                "type": "client_info",
                "client_id": self.client_info[websocket]["id"],
                "info": self.client_info[websocket]
            })
            await self.send(message)

    async def send_to_client(self, websocket, message):
        """向指定客户端发送消息"""
        try:
            await websocket.send(message)
            return True
        except websockets.ConnectionClosed:
            self.clients.discard(websocket)
            if websocket in self.client_info:
                del self.client_info[websocket]
            await self.broadcast_client_list()
            return False


    async def start(self):
        print(f"启动 WebSocket 服务器: ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):  # pyright: ignore[reportArgumentType]
            await asyncio.Future()  # 持续运行直到手动停止

async def main():
    # 创建 WebSocket 服务器实例
    websocket_server = WebSocketServer()
    await websocket_server.start()  # 启动 WebSocket 服务器



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("服务器手动停止")



