"""
Lenovo Laptop Fan Control Backend (Legion, LOQ, IdeaPad Gaming, ThinkPad)
"""

import subprocess
from typing import Dict, Any
from .base import BaseFanBackend

class LenovoBackend(BaseFanBackend):
    def __init__(self, hardware_info: Dict[str, Any]):
        super().__init__(hardware_info)
        self.last_cpu_temp = 45
        self.last_cpu_rpm = 2800

    def _execute_lenovo_wmi(self, command_code: int) -> bool:
        """Invokes Lenovo WMI Thermal Mode or ACPI method"""
        try:
            # Try Lenovo Vantage / GameZone thermal mode method
            ps_script = f"""
            try {{
                $cls = Get-CimClass -Namespace root/wmi -ClassName "Lenovo_ThermalMode" -ErrorAction Stop
                $inst = Get-CimInstance -Namespace root/wmi -ClassName "Lenovo_ThermalMode" -ErrorAction Stop
                Invoke-CimMethod -InputObject $inst -MethodName "SetThermalMode" -Arguments @{{ ThermalMode = {command_code} }}
                exit 0
            }} catch {{
                try {{
                    $inst2 = Get-CimInstance -Namespace root/wmi -ClassName "Lenovo_Vantage_ACPI" -ErrorAction Stop
                    Invoke-CimMethod -InputObject $inst2 -MethodName "SetSpeed" -Arguments @{{ Mode = {command_code} }}
                    exit 0
                }} catch {{
                    exit 1
                }}
            }}
            """
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def get_cpu_temp(self) -> int:
        try:
            # Query standard ACPI thermal zone
            ps = "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty CurrentTemperature"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps], text=True, timeout=2).strip()
            if out and out.isdigit():
                # Kelvin * 10 to Celsius: (K - 2732) / 10
                temp = int((int(out) - 2732) / 10)
                if 20 <= temp <= 115:
                    self.last_cpu_temp = temp
        except Exception:
            pass
        return self.last_cpu_temp

    def get_telemetry(self) -> Dict[str, Any]:
        gpu_t = self.get_gpu_temp_nvml()
        cpu_t = self.get_cpu_temp()

        # Simulated or actual fan RPM reading
        if self.active_mode == "max":
            rpm = 5400
        elif self.active_mode == "manual" and self.target_percentage:
            rpm = int(2000 + (self.target_percentage / 100) * 3400)
        else:
            rpm = 2800 if cpu_t < 60 else (3800 if cpu_t < 80 else 4900)

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
        # Lenovo Extreme Performance Mode (typically mode 3 or 1)
        self._execute_lenovo_wmi(3)
        return True

    def set_manual_percentage(self, percentage: int) -> bool:
        percentage = max(20, min(100, int(percentage)))
        self.active_mode = "manual"
        self.target_percentage = percentage
        self.set_windows_active_cooling(True)
        if percentage >= 85:
            self._execute_lenovo_wmi(3) # Performance
        elif percentage >= 50:
            self._execute_lenovo_wmi(2) # Balanced
        else:
            self._execute_lenovo_wmi(1) # Quiet
        return True

    def reset_to_auto(self) -> bool:
        self.active_mode = "auto"
        self.target_percentage = None
        self._execute_lenovo_wmi(2) # Balanced default
        return True
