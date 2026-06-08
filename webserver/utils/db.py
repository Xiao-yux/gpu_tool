
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# 初始化数据库
db = SQLAlchemy()

def init_db(app):
    """初始化数据库""" 
    # 配置SQLite数据库
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.dirname(basedir), 'cache.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

class Clineinfo(db.Model):
    '''
    客户端缓存信息
    '''
    __tablename__ = 'client_info'

    wsid = db.Column(db.Integer)  # WebSocket连接ID
    sn = db.Column(db.String(64), primary_key=True, nullable=False)  # 客户端序列号
    manufacturer = db.Column(db.String(64))  # 制造商
    pn = db.Column(db.String(64))  # 产品编号
    ip = db.Column(db.String(16))
    cpuinfo = db.Column(db.String(4096))
    diskinfo = db.Column(db.String(4096))
    netinfo = db.Column(db.String(4096))
    gpuinfo = db.Column(db.String(4096))
    psuinfo = db.Column(db.String(4096))
    meminfo = db.Column(db.String(4096))  # 内存信息
    bmcip = db.Column(db.String(16))  # BMC IP
    last_update = db.Column(db.DateTime, default=datetime.now)  # 最后更新时间

    def __repr__(self):
        return f'<Clineinfo {self.sn}>'

    def to_dict(self):
        return {
            'wsid': self.wsid,
            'sn': self.sn,
            'manufacturer': self.manufacturer,
            'pn': self.pn,
            'ip': self.ip,
            'cpuinfo': self.cpuinfo,
            'diskinfo': self.diskinfo,
            'netinfo': self.netinfo,
            'gpuinfo': self.gpuinfo,
            'psuinfo': self.psuinfo,
            'meminfo': self.meminfo,
            'bmcip': self.bmcip,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_update else None
        }

    @staticmethod
    def update_or_create(client_data):
        """更新或创建客户端信息"""
        sn = client_data.get('SN')
        if not sn:
            return None

        client = Clineinfo.query.get(sn)
        if client:
            # 更新现有记录
            client.wsid = client_data.get('id')
            client.ip = client_data.get('ip')
            client.manufacturer = client_data.get('manufacturer')
            client.pn = client_data.get('pn')
            client.cpuinfo = client_data.get('cpuinfo')
            client.diskinfo = client_data.get('diskinfo')
            client.netinfo = client_data.get('netinfo')
            client.gpuinfo = client_data.get('gpuinfo')
            client.psuinfo = client_data.get('psuinfo')
            client.meminfo = client_data.get('meminfo')
            client.bmcip = client_data.get('bmcip')
            client.last_update = datetime.now()
        else:
            # 创建新记录
            client = Clineinfo(
                wsid=client_data.get('id'),
                sn=sn,
                ip=client_data.get('ip'),
                manufacturer=client_data.get('manufacturer'),
                pn=client_data.get('pn'),
                cpuinfo=client_data.get('cpuinfo'),
                diskinfo=client_data.get('diskinfo'),
                netinfo=client_data.get('netinfo'),
                gpuinfo=client_data.get('gpuinfo'),
                psuinfo=client_data.get('psuinfo'),
                meminfo=client_data.get('meminfo'),
                bmcip=client_data.get('bmcip')
            )
            db.session.add(client)

        db.session.commit()
        return client

    @staticmethod
    def get_by_sn(sn):
        """根据序列号获取客户端信息"""
        return Clineinfo.query.get(sn)

    @staticmethod
    def get_all_clients():
        """获取所有客户端信息"""
        return Clineinfo.query.all()




class TaskList(db.Model):
    '''任务列表'''
    id = db.Column(db.Integer, primary_key=True)  # 任务ID
    name = db.Column(db.String(320), unique=True, nullable=False) #任务名称
    note = db.Column(db.String(320), nullable=True) #任务备注
    time = db.Column(db.String(32), nullable=False) #任务添加时间
    cmdlist = db.Column(db.String(1024), nullable=False) #任务命令列表


    def __repr__(self):
        return f'<TaskList {self.name}>'
    
    @staticmethod
    def query_all_tasks():
        """查询所有任务"""
        return TaskList.query.all()
