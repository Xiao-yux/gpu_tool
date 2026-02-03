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
        alert('任务名称和命令列表不能为空');
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
            alert('任务添加成功');
        } else {
            alert('添加任务失败: ' + data.message);
        }
    } catch (error) {
        console.error('添加任务失败:', error);
        alert('添加任务失败');
    }
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
            alert('任务删除成功');
        } else {
            alert('删除任务失败: ' + data.message);
        }
    } catch (error) {
        console.error('删除任务失败:', error);
        alert('删除任务失败');
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
        row.innerHTML = `
            <td class="task-name">${task.name}</td>
            <td class="task-note">${task.note || '无备注'}</td>
            <td class="task-cmdlist">
                <pre class="task-cmdlist-content">${task.cmdlist}</pre>
            </td>
            <td class="task-time">${task.time}</td>
            <td class="task-actions">
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
