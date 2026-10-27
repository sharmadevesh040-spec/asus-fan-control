# Universal Laptop Fan Speed Controller & Max RPM Booster

A universal, high-performance laptop cooling and fan speed control utility that **automatically detects your laptop's make, model, CPU, and GPU at runtime** and dynamically engages the matching hardware driver.

Whether you run this tool on an **ASUS, Lenovo, Dell/Alienware, HP, Acer, MSI, or any other laptop**, it automatically identifies your machine in milliseconds and gives you direct manual fan speed control, including **100% Maximum Highest Fan RPM (Overboost)**.

---

## 🌟 Universal Laptop Brand Support

| Brand / Family | Detected Models | Engine / Driver Activated |
| :--- | :--- | :--- |
| **ASUS** | TUF Gaming, ROG Strix, Zephyrus, ZenBook, VivoBook | **AsusBackend**: Direct kernel `\\.\ATKACPI` ACPI curve control & fan boost |
| **LENOVO** | Legion (5, 7, Pro), LOQ, IdeaPad Gaming, ThinkPad | **LenovoBackend**: Lenovo Vantage & Legion WMI Extreme / Thermal Modes |
| **DELL / ALIENWARE** | Alienware (m-series, x-series), Dell G15/G16, XPS | **DellBackend**: Alienware G-Mode (F9) / Ultra-Performance WMI |
| **HP** | OMEN (15, 16, 17), Victus, Pavilion Gaming | **HPBackend**: HP OMEN WMI Max Fan Boost & Performance Mode |
| **ACER** | Nitro 5 / 16 / 17, Predator Helios, Triton | **AcerBackend**: Acer PredatorSense / NitroSense Max Fans WMI |
| **MSI** | Raider, Stealth, Katana, Pulse, Vector | **MsiBackend**: MSI Cooler Boost 100% Full Speed |
| **UNIVERSAL** | Any Windows Laptop / Desktop PC | **GenericWindowsBackend**: Windows Active Cooling Policy & NVML Telemetry |

---

## 🚀 Quick Start: 3 Ways to Control Your Fans

### 1. Main Interactive Entry Point (`main.py`)
Run:
```bash
python main.py
```
This automatically displays your detected laptop hardware, CPU, GPU, and active driver, along with an interactive terminal menu:
```text
============================================================
       UNIVERSAL FAN SPEED CONTROLLER & MAX RPM BOOSTER
============================================================
 LAPTOP  : ASUSTeK COMPUTER INC. - ASUS TUF Gaming A15 FA506NCR
 HARDWARE: AMD Ryzen 7 7435HS | NVIDIA GeForce RTX 3050 Laptop GPU
 DRIVER  : AsusBackend (ASUS Engine)
------------------------------------------------------------
 CPU Fan : 4800 RPM  (78°C)
 GPU Fan : 3400 RPM  (63°C)
 Mode    : AUTO
------------------------------------------------------------
 [1] ⚡ Set MAXIMUM Fan Speed (100% Highest RPM)
 [2] 🌐 Launch Web Dashboard GUI (Browser)
 [3] 🔄 Restore Factory Automatic Mode (BIOS)
 [4] 📊 Live Continuous Telemetry Monitor
 [5] 🎛️  Set Custom Speed Percentage (30% - 100%)
 [0] ❌ Exit
------------------------------------------------------------
```

Direct command-line shortcuts:
```bash
python main.py max       # Force 100% Maximum Fan Speed
python main.py auto      # Restore factory BIOS mode
python main.py gui       # Launch the Web Dashboard
python main.py status    # Check live RPM & temps
python main.py 85        # Set manual 85% speed
```

---

### 2. Instant 1-Click Desktop Launchers
- **`MAX_FAN_SPEED.bat`**: Double-click to instantly blast both CPU & GPU fans to **100% Maximum Highest RPM**.
- **`AUTO_FAN_SPEED.bat`**: Double-click to restore normal automatic factory BIOS fan curves.
- **`LAUNCH_DASHBOARD.bat`**: Double-click to launch the Cyberpunk/Gaming Dark Mode Web Dashboard GUI.

---

### 3. Beautiful Web Dashboard GUI
Run `LAUNCH_DASHBOARD.bat` or execute in terminal:
```bash
python server.py
```
Open **`http://localhost:8990`** in your browser.

**Dashboard Features:**
- **Dynamic Hardware Branding**: Automatically shows your laptop manufacturer, exact model name, CPU, and GPU.
- **Huge "MAX SPEED (OVERBOOST)" Button**: 1-click trigger for full 100% PWM fan boost.
- **Real-Time Dual Fan Tachometers**: Live animated rotating fan turbines that spin dynamically to match your physical fan RPM.
- **Precision Manual Speed Dial**: Slider from 30% to 100% with live percentage readout.
- **Speed Presets**:
  - 🚀 **Max Speed (100%)**: Overboost for intense gaming/rendering.
  - ⚡ **Turbo (85%)**: High airflow performance.
  - 🎮 **Performance (70%)**: Balanced gaming acoustics.
  - ⚖️ **Balanced (50%)**: Everyday office & web tasks.
  - 🍃 **Quiet (30%)**: Silent acoustic profile for movies and study.
  - 🔄 **Factory Auto**: Restores default BIOS control.
- **Live RPM & Temperature History Graph**: Real-time canvas telemetry visualization.
- **Keyboard Shortcuts**: Press <kbd>M</kbd> for Max, <kbd>A</kbd> for Auto, <kbd>T</kbd> for Turbo.

---

## ⚙️ Architecture & Technical Details
- **Zero Configuration**: Uses native Windows registry introspection (`winreg`) to query SMBIOS tables in sub-milliseconds without requiring any PowerShell child processes or admin popups.
- **Modular Driver Engine**: Clean pluggable backend architecture (`backends/base.py`, `backends/asus.py`, `backends/lenovo.py`, `backends/dell.py`, `backends/hp.py`, `backends/acer.py`, `backends/msi.py`, `backends/generic.py`).
- **GPU Telemetry**: Direct integration with NVIDIA Management Library (`nvml.dll`) for real-time die temperature on any laptop equipped with an NVIDIA GPU.
- **Zero External Dependencies**: Pure Python standard library (`ctypes`, `winreg`, `struct`, `http.server`).
