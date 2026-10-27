"""
Base Class for Laptop Fan Control Backends
Provides shared telemetry (NVML GPU temp, Windows power cooling policies)
"""

import ctypes
import subprocess
from typing import Dict, Any, Optional

class BaseFanBackend:
    def __init__(self, hardware_info: Dict[str, Any]):
        self.hardware_info = hardware_info
        self.active_mode = "auto"
        self.target_percentage = None
        self.nvml_handle = None
        self.nvml_device = None
        self.init_nvml()

    def init_nvml(self):
        """Initializes NVML (NVIDIA Management Library) for cross-laptop GPU telemetry"""
        try:
            nvml = ctypes.CDLL('nvml.dll')
            if nvml.nvmlInit_v2() == 0:
                device = ctypes.c_void_p()
                if nvml.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(device)) == 0:
                    self.nvml_handle = nvml
                    self.nvml_device = device
        except Exception:
            self.nvml_handle = None
            self.nvml_device = None

    def get_gpu_temp_nvml(self) -> int:
        if self.nvml_handle and self.nvml_device:
            try:
                temp = ctypes.c_uint()
                if self.nvml_handle.nvmlDeviceGetTemperature(self.nvml_device, 0, ctypes.byref(temp)) == 0:
                    return temp.value
            except Exception:
                pass
        return 0

    def set_windows_active_cooling(self, active: bool = True):
        """
        Enables Windows Active Cooling Policy (SYSCOOL = 1)
        Active: Fans spin up and ramp before CPU slows down.
        Passive: CPU slows down before fans spin up.
        """
        val = 1 if active else 0
        try:
            subprocess.run(
                ["powercfg", "/setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "SYSCOOL", str(val)],
                creationflags=0x08000000,
                check=False
            )
            subprocess.run(
                ["powercfg", "/setactive", "SCHEME_CURRENT"],
                creationflags=0x08000000,
                check=False
            )
        except Exception:
            pass

    def get_telemetry(self) -> Dict[str, Any]:
        raise NotImplementedError

    def set_max_speed(self) -> bool:
        raise NotImplementedError

    def set_manual_percentage(self, percentage: int) -> bool:
        raise NotImplementedError

    def set_preset(self, preset: str) -> bool:
        preset = preset.lower().strip()
        if preset in ("max", "highest", "full", "overboost", "100"):
            return self.set_max_speed()
        elif preset in ("turbo", "85"):
            return self.set_manual_percentage(85)
        elif preset in ("performance", "perf", "70"):
            return self.set_manual_percentage(70)
        elif preset in ("balanced", "50"):
            return self.set_manual_percentage(50)
        elif preset in ("silent", "quiet", "30"):
            return self.set_manual_percentage(30)
        elif preset in ("auto", "bios", "default", "reset"):
            return self.reset_to_auto()
        else:
            try:
                pct = int(preset.replace("%", ""))
                return self.set_manual_percentage(pct)
            except ValueError:
                return False

    def reset_to_auto(self) -> bool:
        raise NotImplementedError

    def close(self):
        if self.nvml_handle:
            try:
                self.nvml_handle.nvmlShutdown()
            except Exception:
                pass
            self.nvml_handle = None

    def get_info(self) -> Dict[str, Any]:
        return {
            "backend_name": self.__class__.__name__,
            "hardware": self.hardware_info
        }
