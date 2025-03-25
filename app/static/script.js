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
    taskRow.innerHTML = `
        <td class="url"><a href="${url}" target="_blank">${url}</a></td>
        <td class="title">Loading title...</td>
        <td><span class="status">${data.status}</span></td>
        <td><div class="download-link"></div></td>
    `;
    tasksBody.appendChild(taskRow);

    checkStatus(data.task_id, taskRow);
}

async function checkStatus(taskId, taskRow) {
    const response = await fetch(`/status/${taskId}`);
    const data = await response.json();
    const statusSpan = taskRow.querySelector('.status');
    const downloadLinkDiv = taskRow.querySelector('.download-link');
    const titleCell = taskRow.querySelector('.title');

    statusSpan.textContent = data.status;

    if (data.title && titleCell.textContent === 'Loading title...') {
        titleCell.textContent = data.title; // Обновляем название сразу, как только оно получено
    }

    if (data.status === 'completed') {
        if (data.download_url) {
            downloadLinkDiv.innerHTML = `<a href="${data.download_url}" download>Download</a>`;
            downloadLinkDiv.style.display = 'block';
        }
    } else if (data.status === 'processing') {
        // Можно добавить индикатор, если нужно
    } else if (data.status.includes('error')) {
        statusSpan.style.color = 'red';
    }

    if (!data.status.includes('completed') && !data.status.includes('error')) {
        setTimeout(() => checkStatus(taskId, taskRow), 1000);
    }
}