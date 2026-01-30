from utils.ws import WebSocketServer
from flask import jsonify, request
import asyncio

# 全局WebSocket服务器实例
websocket_server = None

def set_websocket_server(ws_server):
    """设置WebSocket服务器实例"""
    global websocket_server
    websocket_server = ws_server

def register_routes(app):
    """注册所有路由"""
    
    @app.route("/api/ws/clients")
    def get_clients():
        """获取所有连接的客户端列表"""
        if websocket_server:
            clients_list = websocket_server.get_client_list()
            return jsonify({
                "success": True,
                "clients": clients_list
            })
        return jsonify({
            "success": False,
            "message": "WebSocket服务器未运行"
        }), 500

    @app.route("/api/ws/client/<client_id>")
    def get_client_info(client_id):
        """获取指定客户端的详细信息"""
        if websocket_server:
            client_info = websocket_server.get_client_info(client_id)
            if client_info:
                return jsonify({
                    "success": True,
                    "info": client_info
                })
            return jsonify({
                "success": False,
                "message": "客户端不存在"
            }), 404
        return jsonify({
            "success": False,
            "message": "WebSocket服务器未运行"
        }), 500

    @app.route("/api/ws/client/<client_id>/refresh", methods=["POST"])
    def refresh_client_info(client_id):
        """刷新指定客户端的系统信息"""
        if websocket_server and websocket_server.loop:
            try:
                # 在事件循环中运行异步任务
                future = asyncio.run_coroutine_threadsafe(
                    websocket_server.request_client_info(client_id),
                    websocket_server.loop
                )
                result = future.result(timeout=5)
                if result:
                    return jsonify({
                        "success": True,
                        "message": "已请求刷新客户端信息"
                    })
                return jsonify({
                    "success": False,
                    "message": "客户端不存在"
                }), 404
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"刷新失败: {str(e)}"
                }), 500
        return jsonify({
            "success": False,
            "message": "WebSocket服务器未运行"
        }), 500

    @app.route("/api/ws/status")
    def ws_status():
        """获取WebSocket服务器状态"""
        if websocket_server:
            return jsonify({
                "success": True,
                "running": True,
                "clients_count": len(websocket_server.clients)
            })
        return jsonify({
            "success": False,
            "running": False
        })