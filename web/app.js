// ASUS TUF Fan Controller Client Logic

const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 82; // ~515.22
const MAX_RATED_RPM = 6000;

let telemetryHistory = {
  cpuRpm: [],
  gpuRpm: [],
  timestamps: []
};

const MAX_HISTORY_POINTS = 35;
let currentSliderVal = 100;
let isPolling = true;

// DOM Elements
const cpuRpmText = document.getElementById('cpuRpmText');
const gpuRpmText = document.getElementById('gpuRpmText');
const cpuTempText = document.getElementById('cpuTempText');
const gpuTempText = document.getElementById('gpuTempText');
const cpuPwmText = document.getElementById('cpuPwmText');
const gpuPwmText = document.getElementById('gpuPwmText');
const activeModeText = document.getElementById('activeModeText');
const sliderValueText = document.getElementById('sliderValueText');
const manualSlider = document.getElementById('manualSlider');
const heroCard = document.getElementById('heroCard');
const boostBadge = document.getElementById('boostBadge');
const boostBadgeText = document.getElementById('boostBadgeText');
const btnMaxLabel = document.getElementById('btnMaxLabel');

const cpuProgressCircle = document.getElementById('cpuProgressCircle');
const gpuProgressCircle = document.getElementById('gpuProgressCircle');
const cpuFanBlades = document.getElementById('cpuFanBlades');
const gpuFanBlades = document.getElementById('gpuFanBlades');

// Canvas Setup
const canvas = document.getElementById('telemetryCanvas');
const ctx = canvas.getContext('2d');

function init() {
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  startPolling();
  setupKeyboardShortcuts();
}

function resizeCanvas() {
  const container = canvas.parentElement;
  canvas.width = container.clientWidth * window.devicePixelRatio;
  canvas.height = container.clientHeight * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  drawChart();
}

// Polling loop
async function fetchTelemetry() {
  if (!isPolling) return;
  try {
    const res = await fetch('/api/status?t=' + Date.now());
    if (!res.ok) throw new Error('Network error');
    const data = await res.json();
    if (data.success !== false) {
      updateUI(data);
      recordTelemetry(data);
    }
  } catch (err) {
    document.getElementById('linkStatus').innerText = 'RECONNECTING...';
    document.getElementById('linkStatus').style.color = '#ff3b30';
  }
}

function startPolling() {
  fetchTelemetry();
  setInterval(fetchTelemetry, 1000);
}

// Update UI Components
function updateUI(data) {
  document.getElementById('linkStatus').innerText = 'ONLINE';
  document.getElementById('linkStatus').style.color = '#10b981';

  const cpuRpm = data.cpu_rpm || 0;
  const gpuRpm = data.gpu_rpm || 0;
  const cpuTemp = data.cpu_temp || 0;
  const gpuTemp = data.gpu_temp || 0;
  const mode = data.mode || 'auto';

  // Text values
  cpuRpmText.innerText = cpuRpm > 0 ? cpuRpm : '0';
  gpuRpmText.innerText = gpuRpm > 0 ? gpuRpm : '0';
  cpuTempText.innerText = cpuTemp > 0 ? cpuTemp : '--';
  gpuTempText.innerText = gpuTemp > 0 ? gpuTemp : '--';

  // Estimate PWM % based on max rated RPM
  const cpuPwm = Math.min(100, Math.round((cpuRpm / MAX_RATED_RPM) * 100));
  const gpuPwm = Math.min(100, Math.round((gpuRpm / MAX_RATED_RPM) * 100));
  cpuPwmText.innerText = cpuPwm + '%';
  gpuPwmText.innerText = gpuPwm + '%';

  // Update Radial Gauge progress
  const cpuOffset = GAUGE_CIRCUMFERENCE - (Math.min(cpuRpm, MAX_RATED_RPM) / MAX_RATED_RPM) * GAUGE_CIRCUMFERENCE;
  const gpuOffset = GAUGE_CIRCUMFERENCE - (Math.min(gpuRpm, MAX_RATED_RPM) / MAX_RATED_RPM) * GAUGE_CIRCUMFERENCE;
  cpuProgressCircle.style.strokeDashoffset = cpuOffset;
  gpuProgressCircle.style.strokeDashoffset = gpuOffset;

  // Dynamically speed up fan blade animation rotation
  updateBladeSpeed(cpuFanBlades, cpuRpm);
  updateBladeSpeed(gpuFanBlades, gpuRpm);

  // Active Mode presentation
  activeModeText.innerText = mode.toUpperCase();
  updatePresetButtons(mode);

  // Max Speed Hero Visual State
  if (mode === 'max') {
    heroCard.classList.add('active-boost');
    boostBadge.style.background = 'rgba(255, 85, 0, 0.25)';
    boostBadge.style.color = '#ff5500';
    boostBadgeText.innerText = '⚡ MAX OVERBOOST ACTIVE';
    btnMaxLabel.innerText = 'MAX RPM ACTIVE';
  } else {
    heroCard.classList.remove('active-boost');
    boostBadge.style.background = 'rgba(255, 85, 0, 0.12)';
    boostBadge.style.color = '#ff8800';
    boostBadgeText.innerText = 'OVERBOOST READY';
    btnMaxLabel.innerText = 'ACTIVATE MAX RPM';
  }
}

function updateBladeSpeed(elem, rpm) {
  if (!rpm || rpm < 200) {
    elem.style.animationDuration = '10s';
    elem.style.opacity = '0.3';
  } else {
    // 6000 RPM -> ~0.08s per rotation (motion blur)
    // 3000 RPM -> ~0.25s
    // 1000 RPM -> ~0.75s
    const dur = Math.max(0.08, 600 / Math.max(rpm, 100));
    elem.style.animationDuration = dur.toFixed(2) + 's';
    elem.style.opacity = '0.95';
  }
}

function updatePresetButtons(activeMode) {
  const buttons = document.querySelectorAll('.preset-btn');
  buttons.forEach(btn => {
    if (btn.dataset.mode === activeMode) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

// Telemetry History & Canvas Graph
function recordTelemetry(data) {
  telemetryHistory.cpuRpm.push(data.cpu_rpm || 0);
  telemetryHistory.gpuRpm.push(data.gpu_rpm || 0);
  if (telemetryHistory.cpuRpm.length > MAX_HISTORY_POINTS) {
    telemetryHistory.cpuRpm.shift();
    telemetryHistory.gpuRpm.shift();
  }
  drawChart();
}

function drawChart() {
  const width = canvas.parentElement.clientWidth;
  const height = canvas.parentElement.clientHeight;
  ctx.clearRect(0, 0, width, height);

  // Draw grid lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  const steps = 4;
  for (let i = 0; i <= steps; i++) {
    const y = (height / steps) * i;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();

    // RPM label
    const rpmVal = Math.round(MAX_RATED_RPM - (i * (MAX_RATED_RPM / steps)));
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.font = '10px Orbitron';
    ctx.fillText(rpmVal + ' RPM', 10, y - 4);
  }

  if (telemetryHistory.cpuRpm.length < 2) return;

  // Draw CPU Line (Cyan)
  drawLine(telemetryHistory.cpuRpm, '#00f3ff', 'rgba(0, 243, 255, 0.15)', width, height);
  // Draw GPU Line (Purple)
  drawLine(telemetryHistory.gpuRpm, '#a855f7', 'rgba(168, 85, 247, 0.15)', width, height);
}

function drawLine(dataPoints, strokeColor, fillColor, width, height) {
  const stepX = width / (MAX_HISTORY_POINTS - 1);
  const startX = width - (dataPoints.length - 1) * stepX;

  ctx.beginPath();
  dataPoints.forEach((val, idx) => {
    const x = startX + idx * stepX;
    const y = height - (Math.min(val, MAX_RATED_RPM) / MAX_RATED_RPM) * (height - 20) - 10;
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  ctx.strokeStyle = strokeColor;
  ctx.lineWidth = 2.5;
  ctx.shadowColor = strokeColor;
  ctx.shadowBlur = 8;
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Gradient area below line
  ctx.lineTo(startX + (dataPoints.length - 1) * stepX, height);
  ctx.lineTo(startX, height);
  ctx.closePath();
  ctx.fillStyle = fillColor;
  ctx.fill();
}

// User Actions
async function triggerMaxSpeed() {
  try {
    const res = await fetch('/api/set_mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'max' })
    });
    const d = await res.json();
    fetchTelemetry();
  } catch (err) {
    console.error('Failed to set max speed:', err);
  }
}

async function triggerAuto() {
  try {
    const res = await fetch('/api/set_mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'auto' })
    });
    const d = await res.json();
    fetchTelemetry();
  } catch (err) {
    console.error('Failed to reset auto:', err);
  }
}

async function setPreset(mode) {
  try {
    const res = await fetch('/api/set_mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: mode })
    });
    fetchTelemetry();
  } catch (err) {
    console.error('Failed to set preset:', err);
  }
}

function onSliderMove(val) {
  currentSliderVal = val;
  sliderValueText.innerText = val;
}

async function applyManualSlider(val) {
  currentSliderVal = val;
  sliderValueText.innerText = val;
  try {
    await fetch('/api/set_percentage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ percentage: parseInt(val) })
    });
    fetchTelemetry();
  } catch (err) {
    console.error('Failed to apply manual slider:', err);
  }
}

function applyCurrentSlider() {
  applyManualSlider(currentSliderVal);
}

function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    const k = e.key.toLowerCase();
    if (k === 'm') triggerMaxSpeed();
    else if (k === 'a') triggerAuto();
    else if (k === 't') setPreset('turbo');
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
