import inspect
import os

import websockets
import asyncio

from websockets.server import ServerConnection


class WebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()  # 存储所有连接的客户端

    async def handle_client(self, websocket: ServerConnection) -> None:
        path = websocket.request.path  # 想要 URI 从这里拿
        self.clients.add(websocket)
        try:
            async for msg in websocket:
                print(f"收到消息: {msg}")
        except websockets.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)

    def run_cmd(self,msg):
        return os.popen(msg).read()

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


    async def start(self):
        print(f"启动 WebSocket 服务器: ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
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



