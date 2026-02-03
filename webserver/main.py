from flask import Flask, render_template, request
import threading
import asyncio
from utils.ws import WebSocketServer
from utils import routws
from utils.db import init_db

app = Flask(__name__)

# 全局WebSocket服务器实例
websocket_server = None
ws_thread = None

# 初始化数据库
init_db(app)

# 注册路由
routws.register_routes(app)

@app.route("/")
def hello():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/tasks")
def tasks():
    return render_template("tasks.html")

def run_websocket_server():
    """在单独的线程中运行WebSocket服务器"""
    global websocket_server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    websocket_server = WebSocketServer(host="0.0.0.0", port=8765)
    websocket_server.set_event_loop(loop)  # 设置事件循环引用
    websocket_server.set_app(app)  # 设置Flask应用上下文引用
    # 设置路由模块中的WebSocket服务器实例
    routws.set_websocket_server(websocket_server)
    loop.run_until_complete(websocket_server.start())

if __name__ == "__main__":
    # 启动WebSocket服务器线程
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    print("WebSocket服务器已启动在端口8765")
    
    # 启动Flask服务器（关闭debug模式以避免重启）
    app.run(debug=False, host="0.0.0.0", port=80)