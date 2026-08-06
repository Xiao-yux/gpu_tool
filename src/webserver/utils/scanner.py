
import concurrent.futures
import ipaddress
import socket
import ssl
import threading
import time
import urllib.request


class ip_config:
    """扫描网段配置
    ip :  ["str","str",,,]
    """
    ip = ["192.168.9.1/24"]
    off_scan = ["192.168.9.1","192.168.9.2","192.168.9.2","192.168.9.9","192.168.9.10"]
    prot = ["80","443"]
    time = 30   #扫描间隔

class WebScanner:
    """Web服务扫描器"""

    def __init__(self):
        self.scanning = False
        self.results = []
        self.lock = threading.Lock()
        self.scan_thread = None

    def _check_port(self, ip: str, port: int, timeout: float = 2.0) -> bool:
        """检查指定IP和端口是否开放"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _get_web_title(self, url: str, timeout: float = 3.0) -> str:
        """获取网页标题"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0'}
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                # 尝试从响应头获取编码
                content_type = response.headers.get('Content-Type', '')
                charset = 'utf-8'
                if 'charset=' in content_type:
                    charset = content_type.split('charset=')[-1].strip()

                html = response.read().decode(charset, errors='ignore')
                # 简单提取title标签内容
                start = html.find('<title>')
                end = html.find('</title>')
                if start != -1 and end != -1:
                    title = html[start + 7:end].strip()
                    # 清理HTML实体和多余空格
                    import re
                    title = re.sub(r'\s+', ' ', title)
                    if title:
                        return title[:50]  # 限制标题长度
        except Exception as e:
            print(f"获取 {url} 标题失败: {e}")
        return "Web服务"

    def _scan_ip(self, ip: str, ports: list[int]) -> list[dict]:
        """扫描单个IP的所有指定端口"""
        results = []
        for port in ports:
            if self._check_port(ip, port):
                protocol = "https" if port == 443 else "http"
                url = f"{protocol}://{ip}:{port}"
                title = self._get_web_title(url)
                results.append({
                    'ip': ip,
                    'port': port,
                    'url': url,
                    'title': title,
                    'protocol': protocol
                })
        return results

    def scan_network(self, network: str, ports: list[int], max_workers: int = 50) -> list[dict]:
        """扫描指定网段"""
        try:
            network_obj = ipaddress.ip_network(network, strict=False)
            skip_ips = {ip.strip() for ip in ip_config.off_scan if ip.strip()}
            all_results = []

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有IP的扫描任务，跳过屏蔽列表中的IP
                future_to_ip = {}
                for ip in network_obj.hosts():
                    ip_str = str(ip)
                    if ip_str in skip_ips:
                        continue
                    future_to_ip[executor.submit(self._scan_ip, ip_str, ports)] = ip_str

                # 收集结果
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        results = future.result()
                        if results:
                            all_results.extend(results)
                    except Exception as e:
                        print(f"扫描 {ip} 时出错: {e}")

            return all_results
        except Exception as e:
            print(f"扫描网段 {network} 时出错: {e}")
            return []

    def start_continuous_scan(self):
        """启动持续扫描"""
        if self.scan_thread and self.scan_thread.is_alive():
            return

        self.scanning = True
        self.scan_thread = threading.Thread(target=self._continuous_scan_loop, daemon=True)
        self.scan_thread.start()

    def _continuous_scan_loop(self):
        """持续扫描循环"""
        while self.scanning:
            all_results = []
            for network in ip_config.ip:
                print(f"开始扫描网段: {network}")
                ports = [int(p) for p in ip_config.prot]
                results = self.scan_network(network, ports)
                all_results.extend(results)

            with self.lock:
                self.results = all_results

            time.sleep(ip_config.time)

    def stop_scan(self):
        """停止扫描"""
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)

    def get_results(self) -> list[dict]:
        """获取扫描结果"""
        with self.lock:
            return self.results.copy()

class IPPingScanner:
    """IP Ping扫描器"""

    def __init__(self):
        self.scanning = False
        self.results = {}  # 格式: {network: {ip: online_status}}
        self.lock = threading.Lock()
        self.scan_thread = None

    def _ping_ip(self, ip: str, timeout: float = 1.0) -> bool:
        """Ping单个IP地址"""
        try:
            # Windows系统使用-n参数，Linux/Unix使用-c参数
            import platform
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', '-w', str(int(timeout * 1000)), str(ip)]

            import subprocess
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            print(f"Ping {ip} 失败: {e}")
            return False

    def scan_network(self, network: str, max_workers: int = 50) -> dict[str, bool]:
        """扫描指定网段的所有IP"""
        try:
            network_obj = ipaddress.ip_network(network, strict=False)
            skip_ips = {ip.strip() for ip in ip_config.off_scan if ip.strip()}
            ip_results = {}

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有IP的ping任务，跳过屏蔽列表中的IP
                future_to_ip = {}
                for ip in network_obj.hosts():
                    ip_str = str(ip)
                    if ip_str in skip_ips:
                        continue
                    future_to_ip[executor.submit(self._ping_ip, ip_str)] = ip_str

                # 收集结果
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        ip_results[ip] = future.result()
                    except Exception as e:
                        print(f"Ping {ip} 时出错: {e}")
                        ip_results[ip] = False

            return ip_results
        except Exception as e:
            print(f"扫描网段 {network} 时出错: {e}")
            return {}

    def start_continuous_scan(self):
        """启动持续扫描"""
        if self.scan_thread and self.scan_thread.is_alive():
            return

        self.scanning = True
        self.scan_thread = threading.Thread(target=self._continuous_scan_loop, daemon=True)
        self.scan_thread.start()

    def _continuous_scan_loop(self):
        """持续扫描循环"""
        while self.scanning:
            all_results = {}
            for network in ip_config.ip:
                print(f"开始Ping扫描网段: {network}")
                results = self.scan_network(network)
                all_results[network] = results

            with self.lock:
                self.results = all_results

            time.sleep(ip_config.time)

    def stop_scan(self):
        """停止扫描"""
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)

    def get_results(self) -> dict[str, dict[str, bool]]:
        """获取扫描结果"""
        with self.lock:
            return self.results.copy()

# 全局扫描器实例
scanner = WebScanner()
# 启动自动扫描
scanner.start_continuous_scan()
print("自动扫描已启动")

# 全局IP扫描器实例
ip_scanner = IPPingScanner()
# 启动IP扫描
ip_scanner.start_continuous_scan()
print("IP扫描已启动")
print("退出ip扫描")
