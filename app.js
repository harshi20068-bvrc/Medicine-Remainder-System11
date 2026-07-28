/* Medicine Reminder System - Single Page Web Application Engine */

const STORAGE_KEYS = {
  USERS: 'mediremind_users',
  ACTIVE_USER: 'mediremind_active_user',
  MEDICINES: 'mediremind_medicines',
  LOGS: 'mediremind_logs'
};

// Global App State
let state = {
  activeUser: null,
  medicines: [],
  logs: [],
  currentView: 'overview',
  scheduleDate: new Date().toISOString().split('T')[0]
};

// Initial Load Handler
document.addEventListener('DOMContentLoaded', () => {
  initApp();
  startClock();
  initNotificationPermissions();
});

// App Initialization
function initApp() {
  const savedUser = localStorage.getItem(STORAGE_KEYS.ACTIVE_USER);
  if (savedUser) {
    state.activeUser = JSON.parse(savedUser);
    loadUserData();
    showDashboardScreen();
  } else {
    showAuthScreen();
  }
}

// Data Storage Management
function loadUserData() {
  if (!state.activeUser) return;
  
  const allMeds = JSON.parse(localStorage.getItem(STORAGE_KEYS.MEDICINES) || '[]');
  state.medicines = allMeds.filter(m => m.userId === state.activeUser.id);

  const allLogs = JSON.parse(localStorage.getItem(STORAGE_KEYS.LOGS) || '[]');
  state.logs = allLogs.filter(l => l.userId === state.activeUser.id);

  // Generate logs for today if not present
  generateScheduleForDate(state.scheduleDate);
}

function saveData() {
  if (!state.activeUser) return;

  const allMeds = JSON.parse(localStorage.getItem(STORAGE_KEYS.MEDICINES) || '[]');
  const otherMeds = allMeds.filter(m => m.userId !== state.activeUser.id);
  localStorage.setItem(STORAGE_KEYS.MEDICINES, JSON.stringify([...otherMeds, ...state.medicines]));

  const allLogs = JSON.parse(localStorage.getItem(STORAGE_KEYS.LOGS) || '[]');
  const otherLogs = allLogs.filter(l => l.userId !== state.activeUser.id);
  localStorage.setItem(STORAGE_KEYS.LOGS, JSON.stringify([...otherLogs, ...state.logs]));
}

// Authentication Logic
function switchAuthTab(tab) {
  const loginBtn = document.getElementById('tab-login-btn');
  const regBtn = document.getElementById('tab-register-btn');
  const loginForm = document.getElementById('login-form');
  const regForm = document.getElementById('register-form');

  if (tab === 'login') {
    loginBtn.classList.add('active');
    regBtn.classList.remove('active');
    loginForm.style.display = 'block';
    regForm.style.display = 'none';
  } else {
    regBtn.classList.add('active');
    loginBtn.classList.remove('active');
    regForm.style.display = 'block';
    loginForm.style.display = 'none';
  }
}

function handleLogin(e) {
  e.preventDefault();
  const u = document.getElementById('login-username').value.trim();
  const p = document.getElementById('login-password').value.trim();
  const errDiv = document.getElementById('login-error');

  const users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
  const user = users.find(x => x.username.toLowerCase() === u.toLowerCase() && x.password === p);

  if (user) {
    state.activeUser = user;
    localStorage.setItem(STORAGE_KEYS.ACTIVE_USER, JSON.stringify(user));
    loadUserData();
    showDashboardScreen();
    errDiv.style.display = 'none';
  } else {
    errDiv.textContent = 'Invalid username or password.';
    errDiv.style.display = 'block';
  }
}

function handleRegister(e) {
  e.preventDefault();
  const fn = document.getElementById('reg-fullname').value.trim();
  const u = document.getElementById('reg-username').value.trim();
  const p = document.getElementById('reg-password').value.trim();
  const cp = document.getElementById('reg-confirm').value.trim();
  const msgDiv = document.getElementById('reg-msg');

  if (p !== cp) {
    msgDiv.textContent = 'Passwords do not match.';
    msgDiv.style.color = 'var(--danger)';
    msgDiv.style.display = 'block';
    return;
  }

  const users = JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
  if (users.some(x => x.username.toLowerCase() === u.toLowerCase())) {
    msgDiv.textContent = 'Username already exists.';
    msgDiv.style.color = 'var(--danger)';
    msgDiv.style.display = 'block';
    return;
  }

  const newUser = {
    id: Date.now(),
    username: u,
    fullName: fn || u,
    password: p
  };

  users.push(newUser);
  localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));

  msgDiv.textContent = 'Account created successfully! Switching to login...';
  msgDiv.style.color = 'var(--success)';
  msgDiv.style.display = 'block';

  setTimeout(() => {
    switchAuthTab('login');
    document.getElementById('login-username').value = u;
    document.getElementById('register-form').reset();
    msgDiv.style.display = 'none';
  }, 1200);
}

function handleLogout() {
  state.activeUser = null;
  localStorage.removeItem(STORAGE_KEYS.ACTIVE_USER);
  showAuthScreen();
}

function showAuthScreen() {
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('dashboard-screen').style.display = 'none';
}

function showDashboardScreen() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('dashboard-screen').style.display = 'block';
  
  const name = state.activeUser.fullName || state.activeUser.username;
  document.getElementById('user-display-name').textContent = name;
  document.getElementById('user-avatar').textContent = name.charAt(0).toUpperCase();

  switchView('overview');
}

// Navigation & Views
function switchView(viewName) {
  state.currentView = viewName;

  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.view-page').forEach(el => el.classList.remove('active'));

  const navEl = document.getElementById(`nav-${viewName}`);
  const viewEl = document.getElementById(`view-${viewName}`);

  if (navEl) navEl.classList.add('active');
  if (viewEl) viewEl.classList.add('active');

  const titles = {
    overview: 'Overview Dashboard',
    medicines: 'Medicine Management',
    schedule: 'Daily Dose Schedule',
    history: 'History & Adherence Reports'
  };
  document.getElementById('page-title').textContent = titles[viewName] || 'Dashboard';

  if (viewName === 'overview') renderOverviewView();
  if (viewName === 'medicines') renderMedicinesView();
  if (viewName === 'schedule') renderScheduleView();
  if (viewName === 'history') renderHistoryView();
}

// Daily Schedule Generator
function generateScheduleForDate(dateStr) {
  state.medicines.forEach(med => {
    if (med.startDate && med.startDate > dateStr) return;
    
    // Check if log entry already exists
    const exists = state.logs.some(l => l.medicineId === med.id && l.scheduledDate === dateStr);
    if (!exists) {
      state.logs.push({
        id: Date.now() + Math.floor(Math.random() * 1000),
        userId: state.activeUser.id,
        medicineId: med.id,
        medicineName: med.name,
        dosage: med.dosage,
        scheduledDate: dateStr,
        scheduledTime: med.scheduledTime || '08:00',
        status: 'PENDING', // PENDING, TAKEN, MISSED
        markedAt: null,
        notes: ''
      });
    }
  });
  saveData();
}

// Render Overview View
function renderOverviewView() {
  const todayStr = new Date().toISOString().split('T')[0];
  generateScheduleForDate(todayStr);

  const todayLogs = state.logs.filter(l => l.scheduledDate === todayStr);
  const takenCount = todayLogs.filter(l => l.status === 'TAKEN').length;
  const missedCount = todayLogs.filter(l => l.status === 'MISSED').length;
  const totalLogs = todayLogs.length;

  document.getElementById('stat-total-meds').textContent = state.medicines.length;
  document.getElementById('stat-taken-today').textContent = takenCount;
  document.getElementById('stat-missed-today').textContent = missedCount;

  const rate = totalLogs > 0 ? Math.round((takenCount / totalLogs) * 100) : 100;
  document.getElementById('stat-adherence-rate').textContent = `${rate}%`;

  const container = document.getElementById('overview-dose-list');
  if (todayLogs.length === 0) {
    container.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">No medicines scheduled for today. Add a medicine to get started!</div>`;
    return;
  }

  container.innerHTML = todayLogs.map(l => renderDoseCardHTML(l)).join('');
}

// Render Medicines View
function renderMedicinesView() {
  const query = (document.getElementById('search-med-input')?.value || '').toLowerCase();
  const filtered = state.medicines.filter(m => 
    m.name.toLowerCase().includes(query) || m.dosage.toLowerCase().includes(query)
  );

  const grid = document.getElementById('medicines-grid');
  if (filtered.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">No medicines found. Click "Add New Medicine" above to create one.</div>`;
    return;
  }

  grid.innerHTML = filtered.map(m => `
    <div class="med-card">
      <div class="med-header">
        <div>
          <div class="med-name">${escapeHTML(m.name)}</div>
          <div class="med-dosage">💊 ${escapeHTML(m.dosage)}</div>
        </div>
        <span class="badge badge-taken">${escapeHTML(m.frequency)}</span>
      </div>
      <div class="med-details">
        <div>⏰ Scheduled Time: <strong>${escapeHTML(m.scheduledTime || '08:00')}</strong></div>
        <div>📅 Start Date: ${escapeHTML(m.startDate || 'Today')}</div>
        ${m.instructions ? `<div>ℹ️ ${escapeHTML(m.instructions)}</div>` : ''}
      </div>
      <div class="med-actions">
        <button class="btn btn-secondary" onclick="editMedicine(${m.id})">✏️ Edit</button>
        <button class="btn btn-danger" onclick="deleteMedicine(${m.id})">🗑️ Delete</button>
      </div>
    </div>
  `).join('');
}

// Render Schedule View
function renderScheduleView() {
  const datePicker = document.getElementById('schedule-date-picker');
  if (!datePicker.value) datePicker.value = state.scheduleDate;

  state.scheduleDate = datePicker.value;
  generateScheduleForDate(state.scheduleDate);

  document.getElementById('schedule-date-title').textContent = `Schedule for ${state.scheduleDate}`;

  const logs = state.logs.filter(l => l.scheduledDate === state.scheduleDate);
  const container = document.getElementById('schedule-dose-list');

  if (logs.length === 0) {
    container.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">No scheduled doses for ${state.scheduleDate}.</div>`;
    return;
  }

  container.innerHTML = logs.map(l => renderDoseCardHTML(l)).join('');
}

function setScheduleDate(type) {
  const dt = new Date();
  if (type === 'tomorrow') dt.setDate(dt.getDate() + 1);
  const str = dt.toISOString().split('T')[0];

  document.getElementById('schedule-date-picker').value = str;
  renderScheduleView();
}

// Helper to render dose item card
function renderDoseCardHTML(log) {
  let badgeClass = 'badge-pending';
  if (log.status === 'TAKEN') badgeClass = 'badge-taken';
  if (log.status === 'MISSED') badgeClass = 'badge-missed';

  return `
    <div class="dose-card">
      <div class="dose-time">⏰ ${log.scheduledTime}</div>
      <div class="dose-info">
        <h4>${escapeHTML(log.medicineName)} <span class="badge ${badgeClass}">${log.status}</span></h4>
        <p>Dosage: ${escapeHTML(log.dosage)} ${log.notes ? `| Note: ${escapeHTML(log.notes)}` : ''}</p>
      </div>
      <div class="dose-btns">
        <button class="btn btn-success" onclick="openActionModal(${log.id}, 'TAKEN')">✅ Mark Taken</button>
        <button class="btn btn-danger" onclick="openActionModal(${log.id}, 'MISSED')">❌ Mark Missed</button>
      </div>
    </div>
  `;
}

// Render History View
function renderHistoryView() {
  const filter = document.getElementById('history-status-filter').value;
  let logs = [...state.logs];

  if (filter !== 'ALL') {
    logs = logs.filter(l => l.status === filter);
  }

  // Sort latest first
  logs.sort((a, b) => b.scheduledDate.localeCompare(a.scheduledDate));

  const tbody = document.getElementById('history-table-body');
  if (logs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">No history records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = logs.map(l => `
    <tr style="border-bottom: 1px solid var(--border-color);">
      <td style="padding: 0.75rem;">${l.scheduledDate} ${l.scheduledTime}</td>
      <td style="padding: 0.75rem; font-weight: 600;">${escapeHTML(l.medicineName)}</td>
      <td style="padding: 0.75rem;">${escapeHTML(l.dosage)}</td>
      <td style="padding: 0.75rem;"><span class="badge ${l.status === 'TAKEN' ? 'badge-taken' : l.status === 'MISSED' ? 'badge-missed' : 'badge-pending'}">${l.status}</span></td>
      <td style="padding: 0.75rem; color: var(--text-muted);">${l.markedAt || '—'}</td>
      <td style="padding: 0.75rem; color: var(--text-muted);">${escapeHTML(l.notes || '—')}</td>
    </tr>
  `).join('');
}

// Medicine Modal Operations
function openAddMedicineModal() {
  document.getElementById('modal-med-title').textContent = 'Add New Medicine';
  document.getElementById('medicine-form').reset();
  document.getElementById('med-id').value = '';
  document.getElementById('med-start').value = new Date().toISOString().split('T')[0];

  openModal('modal-medicine');
}

function editMedicine(medId) {
  const med = state.medicines.find(m => m.id === medId);
  if (!med) return;

  document.getElementById('modal-med-title').textContent = 'Edit Medicine';
  document.getElementById('med-id').value = med.id;
  document.getElementById('med-name').value = med.name;
  document.getElementById('med-dosage').value = med.dosage;
  document.getElementById('med-frequency').value = med.frequency;
  document.getElementById('med-time').value = med.scheduledTime || '08:00';
  document.getElementById('med-start').value = med.startDate || new Date().toISOString().split('T')[0];
  document.getElementById('med-instructions').value = med.instructions || '';

  openModal('modal-medicine');
}

function saveMedicine(e) {
  e.preventDefault();
  const idVal = document.getElementById('med-id').value;

  const medData = {
    id: idVal ? parseInt(idVal) : Date.now(),
    userId: state.activeUser.id,
    name: document.getElementById('med-name').value.trim(),
    dosage: document.getElementById('med-dosage').value.trim(),
    frequency: document.getElementById('med-frequency').value,
    scheduledTime: document.getElementById('med-time').value,
    startDate: document.getElementById('med-start').value,
    instructions: document.getElementById('med-instructions').value.trim()
  };

  if (idVal) {
    const idx = state.medicines.findIndex(m => m.id === parseInt(idVal));
    if (idx !== -1) state.medicines[idx] = medData;
  } else {
    state.medicines.push(medData);
  }

  saveData();
  closeModal('modal-medicine');
  renderOverviewView();
  renderMedicinesView();
  renderScheduleView();
}

function deleteMedicine(medId) {
  if (!confirm('Are you sure you want to delete this medicine?')) return;

  state.medicines = state.medicines.filter(m => m.id !== medId);
  state.logs = state.logs.filter(l => l.medicineId !== medId);

  saveData();
  renderOverviewView();
  renderMedicinesView();
  renderScheduleView();
}

// Action Log Modal (Mark Taken / Missed)
function openActionModal(logId, status) {
  document.getElementById('action-log-id').value = logId;
  document.getElementById('action-status').value = status;
  document.getElementById('modal-action-title').textContent = `Mark as ${status}`;
  document.getElementById('btn-submit-action').textContent = `Confirm ${status}`;
  document.getElementById('action-notes').value = '';

  openModal('modal-action-note');
}

function submitDoseAction(e) {
  e.preventDefault();
  const logId = parseInt(document.getElementById('action-log-id').value);
  const status = document.getElementById('action-status').value;
  const notes = document.getElementById('action-notes').value.trim();

  const log = state.logs.find(l => l.id === logId);
  if (log) {
    log.status = status;
    log.notes = notes;
    log.markedAt = new Date().toLocaleTimeString();
    saveData();
  }

  closeModal('modal-action-note');
  switchView(state.currentView);
}

// CSV Export
function exportHistoryCSV() {
  if (state.logs.length === 0) {
    alert('No logs available to export.');
    return;
  }

  let csv = 'Date,Time,Medicine,Dosage,Status,MarkedAt,Notes\n';
  state.logs.forEach(l => {
    csv += `"${l.scheduledDate}","${l.scheduledTime}","${l.medicineName}","${l.dosage}","${l.status}","${l.markedAt || ''}","${l.notes || ''}"\n`;
  });

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Medicine_Adherence_Report_${state.activeUser.username}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// Utility Modal Helpers
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function escapeHTML(str) {
  return String(str || '').replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  })[m]);
}

// Live Clock & Reminder Checker
function startClock() {
  setInterval(() => {
    const now = new Date();
    const clock = document.getElementById('clock-display');
    if (clock) clock.textContent = now.toLocaleTimeString();

    // Check for due doses
    checkDueReminders(now);
  }, 1000);
}

let notifiedLogs = new Set();
function checkDueReminders(now) {
  if (!state.activeUser) return;

  const todayStr = now.toISOString().split('T')[0];
  const timeStr = now.toTimeString().substring(0, 5); // HH:MM

  state.logs.forEach(log => {
    if (log.scheduledDate === todayStr && log.scheduledTime === timeStr && log.status === 'PENDING' && !notifiedLogs.has(log.id)) {
      notifiedLogs.add(log.id);
      triggerDoseAlert(log);
    }
  });
}

function initNotificationPermissions() {
  if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
    Notification.requestPermission();
  }
}

function triggerDoseAlert(log) {
  // Web Notification
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`⏰ Medicine Time: ${log.medicineName}`, {
      body: `Dosage: ${log.dosage}. Time to take your medicine!`,
      icon: '💊'
    });
  }

  // Audio Sound Alert via Web Audio API
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5 note
    osc.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (err) {
    console.log('Audio playback error:', err);
  }
}
