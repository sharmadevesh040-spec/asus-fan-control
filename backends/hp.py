"""
HP Laptop Fan Control Backend (OMEN, Victus, Pavilion Gaming)
"""

import subprocess
from typing import Dict, Any
from .base import BaseFanBackend

class HPBackend(BaseFanBackend):
    def __init__(self, hardware_info: Dict[str, Any]):
        super().__init__(hardware_info)
        self.last_cpu_temp = 50

    def _execute_hp_wmi(self, mode: int) -> bool:
        try:
            ps_script = f"""
            try {{
                $hp = Get-CimInstance -Namespace root/wmi -ClassName "HP_ThermalMode" -ErrorAction Stop
                Invoke-CimMethod -InputObject $hp -MethodName "SetThermalMode" -Arguments @{{ Mode = {mode} }}
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
            rpm = 5500
        elif self.active_mode == "manual" and self.target_percentage:
            rpm = int(2200 + (self.target_percentage / 100) * 3300)
        else:
            rpm = 2700 if cpu_t < 60 else (3700 if cpu_t < 80 else 4900)

        return {
            "cpu_rpm": rpm,
            "gpu_rpm": rpm - 200 if rpm > 500 else 0,
            "cpu_temp": cpu_t,
            "gpu_temp": gpu_t,
            "mode": self.active_mode,
            "target_percentage": self.target_percentage
        }

    def set_max_speed(self) -> bool:
        self.active_mode = "max"
        self.target_percentage = 100
        self.set_windows_active_cooling(True)
        self._execute_hp_wmi(1) # HP OMEN Performance / Max Fan
        return True

    def set_manual_percentage(self, percentage: int) -> bool:
        percentage = max(20, min(100, int(percentage)))
        self.active_mode = "manual"
        self.target_percentage = percentage
        self.set_windows_active_cooling(True)
        if percentage >= 85:
            self._execute_hp_wmi(1)
        else:
            self._execute_hp_wmi(0)
        return True

    def reset_to_auto(self) -> bool:
        self.active_mode = "auto"
        self.target_percentage = None
        self._execute_hp_wmi(0) # Default / Balanced
        return True
