import asyncio

from flask import jsonify, request
from utils.db import Clineinfo, TaskList, db
from utils.frprun import FRPRun
from utils.scanner import ip_scanner, scanner

# 创建全局FRPRun实例
frp_runner = FRPRun()

# 全局WebSocket服务器实例
websocket_server = None
print("正在初始化WebSocket服务器实例...")
def set_websocket_server(ws_server):
    """设置WebSocket服务器实例"""
    global websocket_server
    websocket_server = ws_server

def register_routes(app):
    """注册所有路由"""
    
    @app.route("/api/scanner/results")
    def get_scan_results():
        """获取扫描结果"""
        try:
            results = scanner.get_results()
            return jsonify({
                "success": True,
                "results": results,
                "count": len(results)
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取扫描结果失败: {e!s}"
            }), 500

    @app.route("/api/ipscan/results")
    def get_ip_scan_results():
        """获取IP扫描结果"""
        try:
            results = ip_scanner.get_results()
            return jsonify({
                "success": True,
                "results": results
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取IP扫描结果失败: {e!s}"
            }), 500

    @app.route("/api/remote/access", methods=["POST"])
    def enable_remote_access():
        """开启远程访问"""
        try:
            data = request.get_json()
            ip = data.get("ip")
            port = data.get("port", 443)

            if not ip:
                return jsonify({
                    "success": False,
                    "message": "IP地址不能为空"
                }), 400

            # 使用FRPRun开启远程访问
            remote_address = frp_runner.run(ip, port)

            return jsonify({
                "success": True,
                "message": "远程访问已开启",
                "remote_address": remote_address
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"开启远程访问失败: {e!s}"
            }), 500

    @app.route("/api/remote/stop", methods=["POST"])
    def stop_remote_access():
        """停止远程访问"""
        try:
            # 使用FRPRun停止远程访问
            result = frp_runner.stop()
            # 清理配置文件，避免重复添加
            frp_runner.clean_config()

            if result:
                return jsonify({
                    "success": True,
                    "message": "远程访问已停止"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "停止远程访问失败"
                }), 500
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"停止远程访问失败: {e!s}"
            }), 500

    @app.route("/api/ws/clients")
    def get_clients():
        """获取所有连接的客户端列表"""
        if websocket_server:
            clients_list = websocket_server.get_client_list()
            
            # 为每个客户端添加SN信息
            for client in clients_list:
                for ws_client in websocket_server.clients:
                    if ws_client in websocket_server.client_info and websocket_server.client_info[ws_client]["id"] == client["id"]:
                        client["sn"] = websocket_server.client_info[ws_client].get("SN", "")
                        break
            
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
            # 首先尝试从数据库获取客户端信息
            # 获取客户端的SN
            client_sn = None
            for client in websocket_server.clients:
                if client in websocket_server.client_info and websocket_server.client_info[client]["id"] == client_id:
                    client_sn = websocket_server.client_info[client].get("SN")
                    break
            
            if client_sn:
                # 从数据库获取客户端信息
                cached_info = Clineinfo.get_by_sn(client_sn)
                if cached_info:
                    return jsonify({
                        "success": True,
                        "info": cached_info.to_dict(),
                        "from_cache": True
                    })
            
            # 数据库中没有缓存，尝试从WebSocket服务器获取
            client_info = websocket_server.get_client_info(client_id)
            if client_info:
                return jsonify({
                    "success": True,
                    "info": client_info,
                    "from_cache": False
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
                    "message": f"刷新失败: {e!s}"
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

    @app.route("/api/ws/cached_clients")
    def get_cached_clients():
        """获取所有缓存的客户端信息"""
        try:
            clients = Clineinfo.get_all_clients()
            clients_list = [client.to_dict() for client in clients]
            return jsonify({
                "success": True,
                "clients": clients_list
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取缓存客户端信息失败: {e!s}"
            }), 500

    @app.route("/api/ws/offline_clients")
    def get_offline_clients():
        """获取离线客户端列表（数据库中有记录但没有ws连接的客户端）"""
        try:
            # 获取所有缓存的客户端
            all_clients = Clineinfo.get_all_clients()
            
            # 获取当前在线的客户端列表
            online_clients = []
            if websocket_server:
                online_clients = websocket_server.get_client_list()
            
            # 提取在线客户端的SN列表
            online_sns = set()
            for client in online_clients:
                if client.get("sn"):
                    online_sns.add(client["sn"])
            
            # 筛选出离线客户端（数据库中有记录但不在在线列表中）
            offline_clients = []
            for client in all_clients:
                if client.sn not in online_sns:
                    offline_clients.append({
                        "sn": client.sn,
                        "ip": client.ip,
                        "manufacturer": client.manufacturer,
                        "pn": client.pn,
                        "last_update": client.last_update.strftime("%Y-%m-%d %H:%M:%S") if client.last_update else None,
                        "online": False
                    })
            
            return jsonify({
                "success": True,
                "clients": offline_clients
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取离线客户端信息失败: {e!s}"
            }), 500

    @app.route("/api/tasks", methods=["GET"])
    def get_tasks():
        """获取所有任务"""
        try:
            tasks = TaskList.query.all()
            tasks_list = []
            for task in tasks:
                tasks_list.append({
                    "id": task.id,
                    "name": task.name,
                    "note": task.note,
                    "time": task.time,
                    "cmdlist": task.cmdlist
                })
            return jsonify({
                "success": True,
                "tasks": tasks_list
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取任务列表失败: {e!s}"
            }), 500

    @app.route("/api/tasks", methods=["POST"])
    def add_task():
        """添加新任务"""
        try:
            data = request.get_json()
            name = data.get("name")
            note = data.get("note")
            cmdlist = data.get("cmdlist")
            
            if not name or not cmdlist:
                return jsonify({
                    "success": False,
                    "message": "任务名称和命令列表不能为空"
                }), 400
            
            # 获取当前时间
            from datetime import datetime
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 创建新任务
            task = TaskList(
                name=name,
                note=note,
                time=time_str,
                cmdlist=cmdlist
            )
            db.session.add(task)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "任务添加成功",
                "task": {
                    "id": task.id,
                    "name": task.name,
                    "note": task.note,
                    "time": task.time,
                    "cmdlist": task.cmdlist
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"添加任务失败: {e!s}"
            }), 500

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        """删除任务"""
        try:
            task = TaskList.query.get(task_id)
            if not task:
                return jsonify({
                    "success": False,
                    "message": "任务不存在"
                }), 404
            
            db.session.delete(task)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "任务删除成功"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"删除任务失败: {e!s}"
            }), 500

    @app.route("/api/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        """修改任务"""
        try:
            task = TaskList.query.get(task_id)
            if not task:
                return jsonify({
                    "success": False,
                    "message": "任务不存在"
                }), 404

            data = request.get_json()
            name = data.get("name")
            note = data.get("note")
            cmdlist = data.get("cmdlist")

            if not name or not cmdlist:
                return jsonify({
                    "success": False,
                    "message": "任务名称和命令列表不能为空"
                }), 400

            # 更新任务信息
            task.name = name
            task.note = note
            task.cmdlist = cmdlist
            # 更新时间
            from datetime import datetime
            task.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            db.session.commit()

            return jsonify({
                "success": True,
                "message": "任务修改成功",
                "task": {
                    "id": task.id,
                    "name": task.name,
                    "note": task.note,
                    "time": task.time,
                    "cmdlist": task.cmdlist
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"修改任务失败: {e!s}"
            }), 500