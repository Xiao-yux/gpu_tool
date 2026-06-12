import subprocess


class ipmitools:
    """ipmi相关工具"""

    @staticmethod
    def _run(cmd, timeout=30):
        """执行 ipmitool 命令并返回输出

        :param cmd: 要执行的 shell 命令
        :param timeout: 超时时间（秒），防止命令长时间挂起
        :return: 命令的标准输出；执行失败时返回空字符串
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if result.returncode != 0:
                return ""
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""

    @staticmethod
    def sdr():
        """传感器数据"""
        return ipmitools._run('ipmitool sdr')

    @staticmethod
    def fru():
        """电源信息"""
        return ipmitools._run('ipmitool fru')

    @staticmethod
    def lan():
        """lan信息"""
        return ipmitools._run('ipmitool lan print')

    @staticmethod
    def user():
        """用户信息"""
        return ipmitools._run('ipmitool user list 1')
