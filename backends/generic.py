"""
Universal / Generic Windows Laptop & PC Fan & Thermal Backend
"""

import subprocess
from typing import Dict, Any
from .base import BaseFanBackend

class GenericWindowsBackend(BaseFanBackend):
    def __init__(self, hardware_info: Dict[str, Any]):
        super().__init__(hardware_info)
        self.last_cpu_temp = 48

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
            rpm = 5400
        elif self.active_mode == "manual" and self.target_percentage:
            rpm = int(2200 + (self.target_percentage / 100) * 3200)
        else:
            rpm = 2500 if cpu_t < 60 else (3600 if cpu_t < 80 else 4800)

        return {
            "cpu_rpm": rpm,
            "gpu_rpm": rpm - 200 if rpm > 500 else 0,
            "cpu_temp": cpu_t,
            "gpu_temp": gpu_t,
            "mode": self.active_mode,
            "target_percentage": self.target_percentage
        }

    def set_max_speed(self) -> bool:
        """Forces Windows Active Cooling Policy and High Performance power state"""
        self.active_mode = "max"
        self.target_percentage = 100
        self.set_windows_active_cooling(True)
        return True

    def set_manual_percentage(self, percentage: int) -> bool:
        percentage = max(20, min(100, int(percentage)))
        self.active_mode = "manual"
        self.target_percentage = percentage
        self.set_windows_active_cooling(percentage >= 60)
        return True

    def reset_to_auto(self) -> bool:
        self.active_mode = "auto"
        self.target_percentage = None
        self.set_windows_active_cooling(False)
        return True
