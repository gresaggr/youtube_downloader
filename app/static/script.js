// Храним таймеры для каждой задачи
const taskTimers = new Map();

// Очистка таблицы и таймеров при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const tasksBody = document.getElementById('tasks-body');
    tasksBody.innerHTML = ''; // Очищаем таблицу
    taskTimers.clear(); // Очищаем таймеры
    console.log('Page loaded, tasksBody and taskTimers cleared');
});

async function addTask() {
    const url = document.querySelector('.url-input').value;
    const type = document.querySelector('.type-select').value;

    const response = await fetch('/download', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url, format: type === 'audio' ? 'mp3' : 'mp4'})
    });
    const data = await response.json();

    const tasksBody = document.getElementById('tasks-body');
    const taskRow = document.createElement('tr');
    taskRow.dataset.taskId = data.task_id; // Сохраняем task_id в строке
    taskRow.innerHTML = `
        <td class="url"><a href="${url}" target="_blank">${url}</a></td>
        <td class="title">Loading title...</td>
        <td><span class="status">${data.status}</span></td>
        <td><div class="download-link"></div></td>
    `;
    taskRow.dataset.checkStatusPause = data.check_status_pause;
    tasksBody.appendChild(taskRow);

    checkStatus(data.task_id, taskRow);
}

async function checkStatus(taskId, taskRow) {
    // Проверяем, что taskId соответствует строке, чтобы избежать старых вызовов
    if (taskRow.dataset.taskId !== taskId) {
        console.log(`Skipping checkStatus for outdated taskId: ${taskId}`);
        return;
    }

    const response = await fetch(`/status/${taskId}`);
    const data = await response.json();
    const statusSpan = taskRow.querySelector('.status');
    const downloadLinkDiv = taskRow.querySelector('.download-link');
    const titleCell = taskRow.querySelector('.title');

    console.log(`Task ${taskId} status:`, data);

    statusSpan.textContent = data.status;

    if (data.title && titleCell.textContent === 'Loading title...') {
        titleCell.textContent = data.title;
    }

    const statusLower = data.status.toLowerCase();

    if (statusLower === 'completed') {
        if (data.download_url) {
            downloadLinkDiv.innerHTML = `<a href="${data.download_url}" download>Download</a>`;
            downloadLinkDiv.style.display = 'block';
        }
        if (taskTimers.has(taskId)) {
            clearTimeout(taskTimers.get(taskId));
            taskTimers.delete(taskId);
        }
    } else if (statusLower === 'processing') {
        // Можно добавить индикатор, если нужно
    } else if (statusLower.includes('error')) {
        statusSpan.style.color = 'red';
        if (taskTimers.has(taskId)) {
            clearTimeout(taskTimers.get(taskId));
            taskTimers.delete(taskId);
        }
    }

    if (statusLower !== 'completed' && !statusLower.includes('error')) {
        const pause = parseInt(taskRow.dataset.checkStatusPause, 10);
        const timerId = setTimeout(() => checkStatus(taskId, taskRow), pause);
        taskTimers.set(taskId, timerId);
    }
}