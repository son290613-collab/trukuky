let employees = [];

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

/* Employees */
async function loadEmployees() {
  employees = await apiFetch('api/employees.php');
  const tbody = document.getElementById('employee-rows');
  tbody.innerHTML = employees.map((e) => `
    <tr>
      <td>${escapeHtml(e.name)}</td>
      <td><span class="badge ${e.role === 'manager' ? 'badge-good' : 'badge-muted'}">${e.role === 'manager' ? 'Quản lý' : 'Nhân viên'}</span></td>
      ${IS_MANAGER ? `<td><button class="btn btn-sm btn-danger" onclick="deleteEmployee(${e.id})">Xoá</button></td>` : ''}
    </tr>`).join('');

  const assigneeSelect = document.getElementById('task-assignee');
  const scheduleSelect = document.getElementById('s-employee');
  const optionsHtml = employees.map((e) => `<option value="${e.id}">${escapeHtml(e.name)}</option>`).join('');
  assigneeSelect.innerHTML = '<option value="">Chưa giao</option>' + optionsHtml;
  scheduleSelect.innerHTML = optionsHtml;
}

async function deleteEmployee(id) {
  if (!confirmAction('Xoá nhân viên này?')) return;
  await apiFetch('api/employees.php', { method: 'DELETE', body: { id } });
  await loadEmployees();
}

document.getElementById('employee-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await apiFetch('api/employees.php', {
      method: 'POST',
      body: {
        name: document.getElementById('e-name').value,
        email: document.getElementById('e-email').value,
        password: document.getElementById('e-password').value,
        role: document.getElementById('e-role').value,
      },
    });
    closeModal('employee-modal');
    document.getElementById('employee-form').reset();
    await loadEmployees();
  } catch (err) {
    alert(err.message);
  }
});

/* Tasks */
async function loadTasks() {
  const date = document.getElementById('task-date').value || todayStr();
  const tasks = await apiFetch(`api/tasks.php?date=${date}`);
  const wrap = document.getElementById('task-rows');
  if (!tasks.length) {
    wrap.innerHTML = '<div class="empty-state">Chưa có việc nào cho ngày này.</div>';
    return;
  }
  wrap.innerHTML = tasks.map((t) => `
    <div class="check-row ${t.status === 'done' ? 'done' : ''}">
      <input type="checkbox" ${t.status === 'done' ? 'checked' : ''} onchange="toggleTask(${t.id}, this.checked)">
      <span class="check-label">${escapeHtml(t.title)}</span>
      <span class="check-meta">${escapeHtml(t.assignee || 'Chưa giao')}</span>
      <button class="btn btn-sm btn-danger" onclick="deleteTask(${t.id})">Xoá</button>
    </div>`).join('');
}

async function toggleTask(id, checked) {
  await apiFetch('api/tasks.php', { method: 'PUT', body: { id, status: checked ? 'done' : 'pending' } });
  await loadTasks();
}

async function deleteTask(id) {
  await apiFetch('api/tasks.php', { method: 'DELETE', body: { id } });
  await loadTasks();
}

document.getElementById('task-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = document.getElementById('task-title').value;
  const assignedTo = document.getElementById('task-assignee').value || null;
  const date = document.getElementById('task-date').value || todayStr();
  await apiFetch('api/tasks.php', { method: 'POST', body: { title, assigned_to: assignedTo, task_date: date } });
  document.getElementById('task-title').value = '';
  await loadTasks();
});

document.getElementById('task-date').addEventListener('change', loadTasks);

/* Schedules */
async function loadSchedules() {
  const from = todayStr();
  const to = new Date(Date.now() + 6 * 86400000).toISOString().slice(0, 10);
  const rows = await apiFetch(`api/schedules.php?from=${from}&to=${to}`);
  const tbody = document.getElementById('schedule-rows');
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Chưa có lịch làm việc trong tuần này.</td></tr>';
    return;
  }
  tbody.innerHTML = rows.map((s) => `
    <tr>
      <td>${escapeHtml(s.employee_name)}</td>
      <td>${new Date(s.work_date).toLocaleDateString('vi-VN')}</td>
      <td>${s.shift_start ? s.shift_start.slice(0,5) : '?'} - ${s.shift_end ? s.shift_end.slice(0,5) : '?'}</td>
      <td>${escapeHtml(s.note || '')}</td>
      <td><button class="btn btn-sm btn-danger" onclick="deleteSchedule(${s.id})">Xoá</button></td>
    </tr>`).join('');
}

async function deleteSchedule(id) {
  await apiFetch('api/schedules.php', { method: 'DELETE', body: { id } });
  await loadSchedules();
}

document.getElementById('schedule-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await apiFetch('api/schedules.php', {
      method: 'POST',
      body: {
        employee_id: document.getElementById('s-employee').value,
        work_date: document.getElementById('s-date').value,
        shift_start: document.getElementById('s-start').value,
        shift_end: document.getElementById('s-end').value,
        note: document.getElementById('s-note').value,
      },
    });
    document.getElementById('schedule-form').reset();
    await loadSchedules();
  } catch (err) {
    alert(err.message);
  }
});

/* Opening checklist templates (manager only) */
async function loadTemplates() {
  const wrap = document.getElementById('template-rows');
  if (!wrap) return;
  const templates = await apiFetch('api/task_templates.php');
  if (!templates.length) {
    wrap.innerHTML = '<div class="empty-state">Chưa có mục mẫu nào.</div>';
    return;
  }
  wrap.innerHTML = templates.map((t) => `
    <div class="check-row ${t.active == 0 ? 'done' : ''}">
      <input type="checkbox" ${t.active == 1 ? 'checked' : ''} onchange="toggleTemplateActive(${t.id}, '${escapeHtml(t.title).replace(/'/g, "\\'")}', ${t.sort_order}, this.checked)">
      <span class="check-label">${escapeHtml(t.title)}</span>
      <span class="check-meta">Thứ tự ${t.sort_order}</span>
      <button class="btn btn-sm btn-danger" onclick="deleteTemplate(${t.id})">Xoá</button>
    </div>`).join('');
}

async function toggleTemplateActive(id, title, sortOrder, active) {
  await apiFetch('api/task_templates.php', {
    method: 'PUT',
    body: { id, title, sort_order: sortOrder, active },
  });
  await loadTemplates();
}

async function deleteTemplate(id) {
  if (!confirmAction('Xoá mục mẫu này?')) return;
  await apiFetch('api/task_templates.php', { method: 'DELETE', body: { id } });
  await loadTemplates();
}

document.getElementById('template-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await apiFetch('api/task_templates.php', {
      method: 'POST',
      body: {
        title: document.getElementById('tpl-title').value,
        sort_order: Number(document.getElementById('tpl-sort').value) || 0,
      },
    });
    document.getElementById('template-form').reset();
    document.getElementById('tpl-sort').value = 0;
    await loadTemplates();
  } catch (err) {
    alert(err.message);
  }
});

async function generateFromTemplates() {
  const date = document.getElementById('task-date').value || todayStr();
  try {
    const result = await apiFetch('api/task_templates.php', {
      method: 'POST',
      body: { action: 'generate', task_date: date },
    });
    if (result.message) {
      alert(result.message);
    } else {
      alert(`Đã tạo ${result.created} mục checklist từ mẫu.`);
    }
    await loadTasks();
  } catch (err) {
    alert(err.message);
  }
}

document.getElementById('task-date').value = todayStr();
loadEmployees().then(loadTasks);
loadSchedules();
if (IS_MANAGER) loadTemplates();
