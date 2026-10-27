"""
Universal Cross-Laptop Fan Speed Controller
Automatically detects laptop manufacturer, model, and hardware,
selecting the optimal backend driver dynamically.
"""

import sys
import os
from typing import Dict, Any, Optional

from hardware_detector import detect_hardware
from backends.base import BaseFanBackend
from backends.asus import AsusBackend
from backends.lenovo import LenovoBackend
from backends.dell import DellBackend
from backends.hp import HPBackend
from backends.acer import AcerBackend
from backends.msi import MsiBackend
from backends.generic import GenericWindowsBackend

class UniversalFanController:
    _instance = None

    def __init__(self):
        self.hardware = detect_hardware()
        self.vendor = self.hardware.get("vendor", "generic")
        self.backend: BaseFanBackend = self._create_backend()

    def _create_backend(self) -> BaseFanBackend:
        """Instantiates the optimal hardware driver based on detected laptop brand"""
        try:
            if self.vendor == "asus":
                return AsusBackend(self.hardware)
            elif self.vendor == "lenovo":
                return LenovoBackend(self.hardware)
            elif self.vendor == "dell":
                return DellBackend(self.hardware)
            elif self.vendor == "hp":
                return HPBackend(self.hardware)
            elif self.vendor == "acer":
                return AcerBackend(self.hardware)
            elif self.vendor == "msi":
                return MsiBackend(self.hardware)
        except Exception as e:
            # Fallback to generic if vendor backend fails to initialize
            print(f"[*] Vendor backend ({self.vendor}) init warning: {e}. Falling back to universal Windows cooling.")
        
        return GenericWindowsBackend(self.hardware)

    # Proxy methods to the active backend
    def get_telemetry(self) -> Dict[str, Any]:
        data = self.backend.get_telemetry()
        data["hardware"] = self.hardware
        return data

    def set_max_speed(self) -> bool:
        return self.backend.set_max_speed()

    def set_manual_percentage(self, percentage: int) -> bool:
        return self.backend.set_manual_percentage(percentage)

    def set_preset(self, preset: str) -> bool:
        return self.backend.set_preset(preset)

    def reset_to_auto(self) -> bool:
        return self.backend.reset_to_auto()

    def close(self):
        if self.backend:
            self.backend.close()

    @property
    def active_mode(self) -> str:
        return self.backend.active_mode

    @property
    def target_percentage(self) -> Optional[int]:
        return self.backend.target_percentage

    def get_info(self) -> Dict[str, Any]:
        return {
            "hardware": self.hardware,
            "backend": self.backend.__class__.__name__,
            "mode": self.active_mode,
            "target": self.target_percentage
        }

if __name__ == "__main__":
    ctrl = UniversalFanController()
    info = ctrl.get_info()
    print("=== Universal Fan Controller ===")
    print(f"  Laptop Detected : {info['hardware']['manufacturer']} - {info['hardware']['model']}")
    print(f"  Processor       : {info['hardware']['cpu']}")
    print(f"  Graphics        : {info['hardware']['primary_gpu']}")
    print(f"  Active Driver   : {info['backend']}")
    print("--------------------------------")
    t = ctrl.get_telemetry()
    print(f"  CPU Fan Speed   : {t['cpu_rpm']} RPM ({t['cpu_temp']}°C)")
    print(f"  GPU Fan Speed   : {t['gpu_rpm']} RPM ({t['gpu_temp']}°C)")
    print(f"  Current Mode    : {t['mode'].upper()}")
    ctrl.close()
