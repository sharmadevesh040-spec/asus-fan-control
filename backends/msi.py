"""
MSI Laptop Fan Control Backend (Cooler Boost, Raider, Stealth, Katana, Pulse)
"""

import subprocess
from typing import Dict, Any
from .base import BaseFanBackend

class MsiBackend(BaseFanBackend):
    def __init__(self, hardware_info: Dict[str, Any]):
        super().__init__(hardware_info)
        self.last_cpu_temp = 50

    def _execute_msi_cooler_boost(self, enable: bool) -> bool:
        try:
            val = 1 if enable else 0
            ps_script = f"""
            try {{
                $msi = Get-CimInstance -Namespace root/wmi -ClassName "MSI_ThermalCenter" -ErrorAction Stop
                Invoke-CimMethod -InputObject $msi -MethodName "SetCoolerBoost" -Arguments @{{ Enable = {val} }}
                exit 0
            }} catch {{
                exit 1
            }}
            """
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def get_cpu_temp(self) -> int:
        try:
            ps = "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty CurrentTemperature"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps], text=True, timeout=2).strip()
            if out and out.isdigit():
                temp = int((int(out) - 2732) / 10)
                if 20 <= temp <= 115:
                    self.last_cpu_temp = temp
        except Exception:
            pass
        return self.last_cpu_temp

    def get_telemetry(self) -> Dict[str, Any]:
        gpu_t = self.get_gpu_temp_nvml()
        cpu_t = self.get_cpu_temp()

        if self.active_mode == "max":
            rpm = 6000 # MSI Cooler Boost typically runs 6000 RPM
        elif self.active_mode == "manual" and self.target_percentage:
            rpm = int(2400 + (self.target_percentage / 100) * 3600)
        else:
            rpm = 2900 if cpu_t < 60 else (4000 if cpu_t < 80 else 5200)

        return {
            "cpu_rpm": rpm,
            "gpu_rpm": rpm,
            "cpu_temp": cpu_t,
            "gpu_temp": gpu_t,
            "mode": self.active_mode,
            "target_percentage": self.target_percentage
        }

    def set_max_speed(self) -> bool:
        """Triggers MSI Cooler Boost (100% full speed)"""
        self.active_mode = "max"
        self.target_percentage = 100
        self.set_windows_active_cooling(True)
        self._execute_msi_cooler_boost(True)
        return True

    def set_manual_percentage(self, percentage: int) -> bool:
        percentage = max(20, min(100, int(percentage)))
        self.active_mode = "manual"
        self.target_percentage = percentage
        self.set_windows_active_cooling(True)
        if percentage >= 90:
            self._execute_msi_cooler_boost(True)
        else:
            self._execute_msi_cooler_boost(False)
        return True

    def reset_to_auto(self) -> bool:
        self.active_mode = "auto"
        self.target_percentage = None
        self._execute_msi_cooler_boost(False)
        return True
