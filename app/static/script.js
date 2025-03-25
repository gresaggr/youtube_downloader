console.log('Script loaded');

async function addTask() {
    const url = document.querySelector('.url-input').value;
    const type = document.querySelector('.type-select').value;

    const response = await fetch('/download', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url, format: type === 'audio' ? 'mp3' : 'mp4'})
    });
    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || "Failed to add task");
        return;
    }

    const tasksBody = document.getElementById('tasks-body');
    const taskRow = document.createElement('tr');
    taskRow.dataset.taskId = data.task_id;
    taskRow.innerHTML = `
        <td class="url"><a href="${url}" target="_blank">${url}</a></td>
        <td class="title">Loading title...</td>
        <td><span class="status">${data.status}</span></td>
        <td><div class="download-link"></div></td>
    `;
    taskRow.dataset.checkStatusPause = data.check_status_pause || 1000;
    tasksBody.appendChild(taskRow);

    console.log(`Task added: ${data.task_id}`);
    checkStatus(data.task_id, taskRow);
}

async function checkStatus(taskId, taskRow) {
    const response = await fetch(`/status/${taskId}`);
    const data = await response.json();
    console.log(`Status for ${taskId}:`, data);

    const statusSpan = taskRow.querySelector('.status');
    const downloadLinkDiv = taskRow.querySelector('.download-link');
    const titleCell = taskRow.querySelector('.title');

    statusSpan.textContent = data.status;

    if (data.title && titleCell.textContent === 'Loading title...') {
        titleCell.textContent = data.title;
    }

    const statusLower = data.status.toLowerCase();
    if (statusLower === 'completed' && data.download_url) {
        downloadLinkDiv.innerHTML = `<a href="${data.download_url}" download>Download</a>`;
        downloadLinkDiv.style.display = 'block';
    } else if (statusLower === 'error') {
        statusSpan.style.color = 'red';
        if (data.error) {
            statusSpan.title = data.error; // Показываем ошибку при наведении
        }
    } else if (statusLower !== 'completed') {
        const pause = parseInt(taskRow.dataset.checkStatusPause, 10);
        setTimeout(() => checkStatus(taskId, taskRow), pause);
    }
}