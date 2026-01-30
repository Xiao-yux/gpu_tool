// API 客户端 - 使用 HTTP 请求获取客户端数据
let clients = {};
let currentClient = null;
let refreshInterval = null;

// 获取客户端列表
async function fetchClientList() {
    try {
        const response = await fetch('/api/ws/clients');
        const data = await response.json();
        console.log("date:"+data);
        
        if (data.success) {
            updateClientList(data.clients);
        }
    } catch (error) {
        console.error('获取客户端列表失败:', error);
    }
}

// 获取指定客户端信息
async function fetchClientInfo(clientId) {
    try {
        const response = await fetch(`/api/ws/client/${clientId}`);
        const data = await response.json();
        console.log("client info data:", data);
        if (data.success) {
            updateClientInfo(clientId, data.info);
        }
    } catch (error) {
        console.error('获取客户端信息失败:', error);
    }
}

// 刷新客户端信息
async function refreshClientInfo(clientId) {
    try {
        const response = await fetch(`/api/ws/client/${clientId}/refresh`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            // 等待一小段时间后重新获取信息
            setTimeout(() => fetchClientInfo(clientId), 500);
        }
    } catch (error) {
        console.error('刷新客户端信息失败:', error);
    }
}

// 更新客户端列表
function updateClientList(clientsList) {
    const clientsListEl = document.getElementById('clientsList');
    const countEl = document.querySelector('.clients-count');

    clientsListEl.innerHTML = '';
    countEl.textContent = clientsList.length + ' 个客户端';

    clientsList.forEach(client => {
        const clientEl = document.createElement('div');
        clientEl.className = 'client-card';
        clientEl.dataset.clientId = client.id;
        clientEl.innerHTML = `
            <div class="client-avatar">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="client-info">
                <div class="client-ip">${client.ip}</div>
                <div class="client-status ${client.online ? 'online' : 'offline'}">${client.online ? '在线' : '离线'}</div>
            </div>
        `;

        clientEl.addEventListener('click', () => showClientDetails(client.id));
        clientsListEl.appendChild(clientEl);
    });
}

// 显示客户端详情
function showClientDetails(clientId) {
    currentClient = clientId;
    const panel = document.getElementById('clientDetailsPanel');
    const tmp = document.getElementById('conn1');
    tmp.style.display = 'none';
    // 立即刷新客户端信息
    refreshClientInfo(clientId);

    panel.style.display = 'block';

    // 设置自动刷新
    // if (refreshInterval) {
    //     clearInterval(refreshInterval);
    // }
    // refreshInterval = setInterval(() => {
    //     if (currentClient) {
    //         refreshClientInfo(currentClient);
    //     }
    // }, 5000); // 每5秒刷新一次
}

// 更新客户端信息
function updateClientInfo(clientId, info) {
    clients[clientId] = { ...clients[clientId], ...info };

    if (currentClient === clientId) {
        console.log(info);
        
        document.getElementById('detailIp').textContent = info.ip || '-';
        document.getElementById('detailSN').textContent = info.SN || '-';
        document.getElementById('detailTime').textContent = info.time || '-';

        // 更新当前选项卡内容
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab) {
            const tabName = activeTab.dataset.tab;
            const content = document.getElementById('tabContentText');
            content.textContent = clients[currentClient][tabName] || '暂无数据';
        }
    }
}

// 关闭详情面板
function closeDetails() {
    document.getElementById('clientDetailsPanel').style.display = 'none';
    currentClient = null;
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    const tmp = document.getElementById('conn1');
    tmp.style.display = '';
}

// 选项卡切换
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        const tabName = this.dataset.tab;
        const content = document.getElementById('tabContentText');

        if (currentClient && clients[currentClient]) {
            content.textContent = clients[currentClient][tabName] || '暂无数据';
            // 切换选项卡时刷新客户端信息
            refreshClientInfo(currentClient);
        } else {
            content.textContent = '请选择一个客户端';
        }
    });
});

// 页面加载完成后，开始定期获取客户端列表
document.addEventListener('DOMContentLoaded', () => {
    // 立即获取一次客户端列表
    fetchClientList();
    // 每3秒获取一次客户端列表
    setInterval(fetchClientList, 3000);
});
