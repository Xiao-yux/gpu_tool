

// 任务管理功能
let tasks = [];
let currentPage = 1;
let itemsPerPage = 10; // 每页显示的指令数量

// 获取所有任务

async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        if (data.success) {
            tasks = data.tasks;
            renderTasks();
            updatePagination();
        } else {
            console.error('获取任务列表失败:', data.message);
        }
    } catch (error) {
        console.error('获取任务列表失败:', error);
    }
}

// 切换添加任务表单的显示/隐藏
function toggleAddTaskForm() {
    const form = document.getElementById('addTaskForm');
    if (form.style.display === 'none') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

// 添加新任务
async function addTask() {
    const name = document.getElementById('taskName').value.trim();
    const note = document.getElementById('taskNote').value.trim();
    const cmdlist = document.getElementById('taskCmdlist').value.trim();

    if (!name || !cmdlist) {
        swal('', '任务名称和命令列表不能为空', 'error');
        return;
    }

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                note: note,
                cmdlist: cmdlist
            })
        });
        const data = await response.json();
        if (data.success) {
            // 清空表单
            document.getElementById('taskName').value = '';
            document.getElementById('taskNote').value = '';
            document.getElementById('taskCmdlist').value = '';

            // 隐藏表单
            toggleAddTaskForm();

            // 重新获取任务列表
            await fetchTasks();
            showmessg('任务添加成功', 'success');
        } else {
            showmessg('添加任务失败: ' + data.message);
        }
    } catch (error) {
        console.error('添加任务失败:', error);
        showmessg('添加任务失败');
    }
}

//弹窗
function showmessg(message, type = 'error') {
    swal( "Ops" ,  message ,  type );
}

// 删除任务
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
            // 重新获取任务列表
            await fetchTasks();
            showmessg('任务删除成功', 'success');
        } else {
            showmessg('删除任务失败: ' + data.message);
        }
    } catch (error) {
        console.error('删除任务失败:', error);
        showmessg('删除任务失败');
    }
}

// 显示编辑任务表单
function showEditTaskForm(taskId) {
    // 查找要编辑的任务
    const task = tasks.find(t => t.id === taskId);
    if (!task) {
        showmessg('找不到任务');
        return;
    }

    // 隐藏添加任务表单
    document.getElementById('addTaskForm').style.display = 'none';

    // 填充编辑表单
    document.getElementById('editTaskId').value = task.id;
    document.getElementById('editTaskName').value = task.name;
    document.getElementById('editTaskNote').value = task.note || '';
    document.getElementById('editTaskCmdlist').value = task.cmdlist;

    // 显示编辑表单
    document.getElementById('editTaskForm').style.display = 'block';
}

// 隐藏编辑任务表单
function hideEditTaskForm() {
    document.getElementById('editTaskForm').style.display = 'none';
}

// 修改任务
async function editTask() {
    const taskId = document.getElementById('editTaskId').value;
    const name = document.getElementById('editTaskName').value.trim();
    const note = document.getElementById('editTaskNote').value.trim();
    const cmdlist = document.getElementById('editTaskCmdlist').value.trim();

    if (!name || !cmdlist) {
        alert('任务名称和命令列表不能为空');
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                note: note,
                cmdlist: cmdlist
            })
        });
        const data = await response.json();
        if (data.success) {
            // 隐藏编辑表单
            hideEditTaskForm();
            // 重新获取任务列表
            await fetchTasks();
            showmessg('任务修改成功', 'success'); 
        } else {
            showmessg('修改任务失败: ' + data.message);
        }
    } catch (error) {
        console.error('修改任务失败:', error);
        showmessg('修改任务失败');
    }
}

// 渲染任务列表
function renderTasks() {
    const tasksTableBody = document.getElementById('tasksTableBody');
    if (!tasksTableBody) return;
    
    tasksTableBody.innerHTML = '';
    
    if (tasks.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="no-tasks">暂无任务</td>';
        tasksTableBody.appendChild(row);
        return;
    }
    
    // 计算当前页的任务
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, tasks.length);
    const currentTasks = tasks.slice(startIndex, endIndex);
    
    // 渲染当前页的任务
    currentTasks.forEach(task => {
        const row = document.createElement('tr');
        
        // 创建命令列表单元格
        const cmdlistCell = document.createElement('td');
        cmdlistCell.className = 'task-cmdlist';
        
        // 创建命令列表内容元素
        const cmdlistContent = document.createElement('pre');
        cmdlistContent.className = 'task-cmdlist-content';
        cmdlistContent.textContent = task.cmdlist.replace(/\n/g, ' ');
        
        // 添加鼠标悬停事件
        cmdlistContent.addEventListener('mouseenter', function(e) {
            // 创建工具提示
            const tooltip = document.createElement('div');
            tooltip.className = 'task-cmdlist-tooltip';
            tooltip.textContent = task.cmdlist;
            
            // 设置工具提示位置
            const rect = this.getBoundingClientRect();
            tooltip.style.left = (rect.left + rect.width / 2) + 'px';
            tooltip.style.top = (rect.top - 10) + 'px';
            
            // 添加到文档
            document.body.appendChild(tooltip);
            
            // 保存工具提示引用
            this._tooltip = tooltip;
        });
        
        // 添加鼠标离开事件
        cmdlistContent.addEventListener('mouseleave', function() {
            // 移除工具提示
            if (this._tooltip) {
                document.body.removeChild(this._tooltip);
                this._tooltip = null;
            }
        });
        
        // 将命令列表内容添加到单元格
        cmdlistCell.appendChild(cmdlistContent);
        
        // 设置其他单元格内容
        row.innerHTML = `
            <td class="task-name">${task.name}</td>
            <td class="task-note">${task.note || '无备注'}</td>
        `;
        
        // 添加命令列表单元格
        row.appendChild(cmdlistCell);
        
        // 添加时间和操作列
        row.innerHTML += `
            <td class="task-time">${task.time}</td>
            <td class="task-actions">
                <button class="edit-task-btn" onclick="showEditTaskForm(${task.id})">修改</button>
                <button class="delete-task-btn" onclick="deleteTask(${task.id})">删除</button>
            </td>
        `;
        
        tasksTableBody.appendChild(row);
    });
}

// 更新分页信息
function updatePagination() {
    const totalPages = Math.ceil(tasks.length / itemsPerPage) || 1;
    
    // 更新当前页码
    document.getElementById('currentPage').textContent = currentPage;
    
    // 更新总页数
    document.getElementById('totalPages').textContent = totalPages;
    
    // 更新上一页按钮状态
    document.getElementById('prevPageBtn').disabled = currentPage === 1;
    
    // 更新下一页按钮状态
    document.getElementById('nextPageBtn').disabled = currentPage === totalPages;
}

// 切换页面
function changePage(delta) {
    const totalPages = Math.ceil(tasks.length / itemsPerPage) || 1;
    const newPage = currentPage + delta;
    
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        renderTasks();
        updatePagination();
    }
}

// 页面加载完成后，获取任务列表
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否在任务页面
    if (document.getElementById('tasksPanel')) {
        fetchTasks();
    }
});
