# ASUS TUF Gaming A15 — Fan Speed Controller & Max RPM Booster

A specialized, high-performance fan control utility tailored specifically for your **ASUS TUF Gaming A15 (FA506NCR)** with an **NVIDIA GeForce RTX 3050 Laptop GPU**.

This tool communicates directly with the motherboard's **ASUS Advanced Configuration and Power Interface (`\\.\ATKACPI`)** and NVIDIA management library (`nvml.dll`), allowing you to unlock and manually force the **absolute highest fan RPM** (~5,800+ RPM) or dial custom fan speeds without relying on heavy background software.

---

## 🚀 Quick Start: 3 Ways to Control Your Fans

### 1. Main Interactive Entry Point (`main.py`)
Run:
```bash
python main.py
```
This gives you an interactive menu directly in your terminal to set **Maximum Fan Speed**, launch the **Web GUI**, monitor live RPMs, or dial custom percentages.

You can also pass arguments directly:
```bash
python main.py max       # Force 100% Maximum Fan Speed
python main.py auto      # Restore factory BIOS mode
python main.py gui       # Launch the Web Dashboard
python main.py status    # Check live RPM & temps
python main.py 80        # Set manual 80% speed
```

---

### 2. Instant 1-Click Desktop Launchers
Located right in this folder:
- **`MAX_FAN_SPEED.bat`**: Double-click to instantly blast both CPU & GPU fans to **100% Maximum Highest RPM**.
- **`AUTO_FAN_SPEED.bat`**: Double-click to restore normal automatic factory BIOS fan curves.
- **`LAUNCH_DASHBOARD.bat`**: Double-click to launch the Cyberpunk/TUF Dark Mode Web Dashboard GUI in your browser.

---

### 2. Beautiful Web Dashboard GUI
Run `LAUNCH_DASHBOARD.bat` or execute in terminal:
```bash
python server.py
```
Open **`http://localhost:8990`** in your browser.

**Dashboard Features:**
- **Huge "MAX SPEED (OVERBOOST)" Button**: 1-click trigger for full 100% PWM fan boost.
- **Real-Time Dual Fan Tachometers**: Live animated rotating fan turbines that spin faster or slower matching the actual physical RPM of your CPU and GPU fans.
- **Precision Manual Speed Dial**: Slider from 30% to 100% with live percentage readout.
- **Speed Presets**:
  - 🚀 **Max Speed (100%)**: Overboost for intense gaming/rendering.
  - ⚡ **Turbo (85%)**: High airflow gaming.
  - 🎮 **Performance (70%)**: Balanced gaming thermal profile.
  - ⚖️ **Balanced (50%)**: Everyday office & web tasks.
  - 🍃 **Quiet (30%)**: Silent acoustic profile for movies and quiet rooms.
  - 🔄 **Factory Auto**: Restores ASUS default BIOS control.
- **Live RPM & Temperature History Graph**: Real-time canvas telemetry visualization.
- **Keyboard Shortcuts**: Press <kbd>M</kbd> for Max, <kbd>A</kbd> for Auto, <kbd>T</kbd> for Turbo.

---

### 3. Command Line Interface (CLI)
You can control the fans directly from any Command Prompt or PowerShell window:

```cmd
# Blast fans to maximum highest RPM
fan max

# Restore default automatic BIOS mode
fan auto

# Set custom manual percentage (30% to 100%)
fan 80
fan 65

# Preset shortcuts
fan turbo
fan balanced
fan silent

# View live RPM and temperatures
fan status

# Real-time continuous terminal monitoring
fan monitor
```

---

## ⚙️ Technical Details
- **Driver Interface**: Interacts with the kernel device `\\.\ATKACPI` via IOCTL `0x0022240C` using method calls `DEVS` and `DSTS`.
- **Fan Curve Mapping**: Writes 16-byte custom temperature-to-speed curve arrays to `0x00110024` (CPU Fan Curve) and `0x00110025` (GPU Fan Curve).
- **Fan Boost Flag**: Pulses ACPI Device `0x00110013` (CPU Fan Boost) & `0x00110014` (GPU Fan Boost) to signal maximum diagnostic RPM to the embedded controller (EC).
- **Telemetry Sensors**: Direct query of CPU fan RPM (`0x00110013`), GPU fan RPM (`0x00110014`), CPU core temperature (`0x00120094`), and GPU die temperature via `nvml.dll`.
- **Zero External Dependencies**: Implemented in pure Python using `ctypes` and standard libraries.
