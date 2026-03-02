// API 客户端 - 使用 HTTP 请求获取客户端数据
let clients = {};
let currentClient = null;
let currentOfflineClient = null;
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
        // 添加加载状态
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
            refreshBtn.disabled = true;
        }
        
        const response = await fetch(`/api/ws/client/${clientId}/refresh`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            // 等待一小段时间后重新获取信息
            setTimeout(() => {
                fetchClientInfo(clientId);
                // 移除加载状态
                if (refreshBtn) {
                    refreshBtn.classList.remove('loading');
                    refreshBtn.disabled = false;
                }
            }, 500);
        } else {
            // 移除加载状态
            if (refreshBtn) {
                refreshBtn.classList.remove('loading');
                refreshBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error('刷新客户端信息失败:', error);
        // 移除加载状态
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.classList.remove('loading');
            refreshBtn.disabled = false;
        }
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
                <div class="client-sn">${client.sn || "-"}</div>
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
    
    // 先尝试获取缓存的客户端信息
    fetchClientInfo(clientId);
    
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

// 刷新当前客户端信息
function refreshCurrentClient() {
    if (currentClient) {
        refreshClientInfo(currentClient);
    }
}

// 更新客户端信息
function updateClientInfo(clientId, info) {
    clients[clientId] = { ...clients[clientId], ...info };

    if (currentClient === clientId) {
        console.log(info);
        
        document.getElementById('detailIp').textContent = info.bmcip || '-';
        document.getElementById('detailSN').textContent = info.sn || info.SN || '-';
        document.getElementById('detailTime').textContent = info.last_update || info.time || '-';
        document.getElementById('detailManufacturer').textContent = info.manufacturer || '-';
        document.getElementById('detailPn').textContent = info.pn || '-';
        
        // 确保SN字段在客户端对象中正确设置
        if (info.sn && !info.SN) {
            clients[clientId].SN = info.sn;
        }

        // 更新当前选项卡内容
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab) {
            const tabName = activeTab.dataset.tab;
            updateTabContent(tabName);
        }
    }
}

// 更新选项卡内容
function updateTabContent(tabName) {
    if (!currentClient || !clients[currentClient]) {
        return;
    }

    const clientData = clients[currentClient];

    // 根据不同的选项卡更新对应的内容区域
    switch(tabName) {
        case 'cpuinfo':
            const cpuContent = document.getElementById('tabContentText');
            if (cpuContent) {
                cpuContent.textContent = clientData.cpuinfo || '暂无CPU信息';
            }
            break;
        case 'meminfo':
            const memContent = document.getElementById('tabContentTextMem');
            if (memContent) {
                memContent.textContent = clientData.meminfo || '暂无内存信息';
            }
            break;
        case 'diskinfo':
            const diskContent = document.getElementById('tabContentTextDisk');
            if (diskContent) {
                diskContent.textContent = clientData.diskinfo || '暂无磁盘信息';
            }
            break;
        case 'netinfo':
            const netContent = document.getElementById('tabContentTextNet');
            if (netContent) {
                netContent.textContent = clientData.netinfo || '暂无网络信息';
            }
            break;
        case 'psuinfo':
            const psuContent = document.getElementById('tabContentTextPsu');
            if (psuContent) {
                psuContent.textContent = clientData.psuinfo || '暂无电源信息';
            }
            break;
        case 'gpuinfo':
            const gpuContent = document.getElementById('tabContentTextGpu');
            if (gpuContent) {
                gpuContent.textContent = clientData.gpuinfo || '暂无GPU信息';
            }
            break;
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
document.addEventListener('DOMContentLoaded', () => {

    // 在线客户端选项卡切换
    document.querySelectorAll('.tab-btn:not([data-tab^="offline"])').forEach(btn => {
        btn.addEventListener('click', function() {
            // 移除所有选项卡按钮的active类
            document.querySelectorAll('.tab-btn:not([data-tab^="offline"])').forEach(b => b.classList.remove('active'));
            // 给当前点击的按钮添加active类
            this.classList.add('active');

            const tabName = this.dataset.tab;

            // 隐藏所有在线客户端信息面板
            document.getElementById('cpuinfo').style.display = 'none';
            document.getElementById('meminfo').style.display = 'none';
            document.getElementById('diskinfo').style.display = 'none';
            document.getElementById('netinfo').style.display = 'none';
            document.getElementById('psuinfo').style.display = 'none';
            document.getElementById('gpuinfo').style.display = 'none';

            // 显示选中的信息面板
            const selectedPanel = document.getElementById(tabName);
            if (selectedPanel) {
                selectedPanel.style.display = 'block';
            }

            // 更新选项卡内容
            updateTabContent(tabName);
        });
    });

    // 离线客户端选项卡切换
    document.querySelectorAll('.tab-btn[data-tab^="offline"]').forEach(btn => {
        btn.addEventListener('click', function() {
            // 移除所有离线选项卡按钮的active类
            document.querySelectorAll('.tab-btn[data-tab^="offline"]').forEach(b => b.classList.remove('active'));
            // 给当前点击的按钮添加active类
            this.classList.add('active');

            const tabName = this.dataset.tab;

            // 隐藏所有离线客户端信息面板
            document.getElementById('offlinecpuinfo').style.display = 'none';
            document.getElementById('offlinememinfo').style.display = 'none';
            document.getElementById('offlinediskinfo').style.display = 'none';
            document.getElementById('offlinenetinfo').style.display = 'none';
            document.getElementById('offlinepsuinfo').style.display = 'none';
            document.getElementById('offlinegpuinfo').style.display = 'none';

            // 显示选中的信息面板
            const selectedPanel = document.getElementById(tabName);
            if (selectedPanel) {
                selectedPanel.style.display = 'block';
            }
        });
    });
});

// 获取离线客户端列表
async function fetchOfflineClients() {
    try {
        const response = await fetch('/api/ws/offline_clients');
        const data = await response.json();
        console.log("offline clients data:", data);

        if (data.success) {
            updateOfflineClientsList(data.clients);
        }
    } catch (error) {
        console.error('获取离线客户端列表失败:', error);
    }
}

// 更新离线客户端列表
function updateOfflineClientsList(offlineClientsList) {
    const offlineClientsListEl = document.getElementById('offlineClientsList');
    const countEl = document.getElementById('offlineClientsCount');

    if (!offlineClientsListEl || !countEl) {
        return;
    }

    offlineClientsListEl.innerHTML = '';
    countEl.textContent = offlineClientsList.length + ' 个客户端';

    offlineClientsList.forEach(client => {
        const clientEl = document.createElement('div');
        clientEl.className = 'client-card';
        clientEl.dataset.clientSn = client.sn;
        clientEl.innerHTML = `
            <div class="client-avatar">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="client-info">
                <div class="client-ip">${client.ip || "-"}</div>
                <div class="client-sn">${client.sn || "-"}</div>
                <div class="client-status offline">${"离线"}</div>
            </div>
        `;

        clientEl.addEventListener('click', () => showOfflineClientDetails(client.sn));
        offlineClientsListEl.appendChild(clientEl);
    });
}

// 显示离线客户端详情
function showOfflineClientDetails(clientSn) {
    // 从数据库获取该客户端的详细信息
    fetch(`/api/ws/cached_clients`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const client = data.clients.find(c => c.sn === clientSn);
                if (client) {
                    // 更新离线客户端详情面板的信息
                    document.getElementById('offlineDetailIp').textContent = client.bmcip || '-';
                    document.getElementById('offlineDetailSN').textContent = client.sn || '-';
                    document.getElementById('offlineDetailTime').textContent = client.last_update || '-';
                    document.getElementById('offlineDetailManufacturer').textContent = client.manufacturer || '-';
                    document.getElementById('offlineDetailPn').textContent = client.pn || '-';
                    
                    // 更新各个选项卡的内容
                    document.getElementById('offlineTabContentText').textContent = client.cpuinfo || '暂无CPU信息';
                    document.getElementById('offlineTabContentTextMem').textContent = client.meminfo || '暂无内存信息';
                    document.getElementById('offlineTabContentTextDisk').textContent = client.diskinfo || '暂无磁盘信息';
                    document.getElementById('offlineTabContentTextNet').textContent = client.netinfo || '暂无网络信息';
                    document.getElementById('offlineTabContentTextPsu').textContent = client.psuinfo || '暂无电源信息';
                    document.getElementById('offlineTabContentTextGpu').textContent = client.gpuinfo || '暂无GPU信息';
                    
                    // 显示离线客户端详情面板
                    const panel = document.getElementById('offlineClientDetailsPanel');
                    const tmp = document.getElementById('conn2');
                    tmp.style.display = 'none';
                    panel.style.display = 'block';
                    
                    currentOfflineClient = clientSn;
                }
            }
        })
        .catch(error => {
            console.error('获取离线客户端详情失败:', error);
        });
}

// 关闭离线客户端详情面板
function closeOfflineDetails() {
    document.getElementById('offlineClientDetailsPanel').style.display = 'none';
    currentOfflineClient = null;
    const tmp = document.getElementById('conn2');
    tmp.style.display = '';
}

// 页面加载完成后，开始定期获取客户端列表
document.addEventListener('DOMContentLoaded', () => {
    // 立即获取一次客户端列表
    fetchClientList();
    fetchOfflineClients();
    // 每3秒获取一次客户端列表
    setInterval(fetchClientList, 3000);
    setInterval(fetchOfflineClients, 3000);
});
