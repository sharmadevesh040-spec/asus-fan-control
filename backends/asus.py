"""
ASUS TUF & ROG Laptop Fan Control Backend (Direct ATKACPI Interface)
"""

import ctypes
import struct
import time
import threading
from ctypes import wintypes
from typing import Dict, Any, Optional

from .base import BaseFanBackend

FILE_NAME = r'\\.\ATKACPI'
CONTROL_CODE = 0x0022240C
DSTS = 0x53545344
DEVS = 0x53564544

DEVID_CPU_FAN = 0x00110013
DEVID_GPU_FAN = 0x00110014
DEVID_CPU_FAN_CURVE = 0x00110024
DEVID_GPU_FAN_CURVE = 0x00110025
DEVID_CPU_TEMP = 0x00120094
DEVID_GPU_TEMP = 0x00120097
DEVID_PERF_MODE = 0x00120075

DEFAULT_TEMPS_CPU = [35, 45, 55, 65, 75, 82, 87, 92]
DEFAULT_TEMPS_GPU = [35, 45, 55, 65, 72, 78, 83, 87]

class AsusBackend(BaseFanBackend):
    def __init__(self, hardware_info: Dict[str, Any]):
        super().__init__(hardware_info)
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.handle = None
        self._lock = threading.Lock()
        self.init_driver()

        # Save factory baseline curves
        self.factory_cpu_curve = self.get_curve(DEVID_CPU_FAN_CURVE) or [
            51, 54, 56, 71, 76, 82, 87, 92,
            1, 13, 18, 25, 29, 36, 43, 49
        ]
        self.factory_gpu_curve = self.get_curve(DEVID_GPU_FAN_CURVE) or [
            46, 50, 55, 60, 65, 69, 74, 78,
            1, 13, 19, 26, 30, 37, 44, 51
        ]

        self._keepalive_running = False
        self._keepalive_thread = None

    def init_driver(self):
        with self._lock:
            if self.handle and self.handle != -1:
                return
            CreateFileW = self.kernel32.CreateFileW
            CreateFileW.argtypes = [
                wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p
            ]
            CreateFileW.restype = wintypes.HANDLE
            self.handle = CreateFileW(FILE_NAME, 0xC0000000, 3, None, 3, 0, None)
            if self.handle == -1 or self.handle == 0:
                err = ctypes.get_last_error()
                self.handle = None
                raise RuntimeError(f"Unable to open ATKACPI device: Error code {err}")

    def close(self):
        self.stop_keepalive()
        with self._lock:
            if self.handle and self.handle != -1:
                self.kernel32.CloseHandle(self.handle)
                self.handle = None
        super().close()

    def _call_method(self, method_id: int, dev_id: int, arg2: int = 0) -> int:
        with self._lock:
            if not self.handle:
                self.init_driver()
            in_buf = struct.pack('<IIII', method_id, 8, dev_id, arg2)
            out_buf = ctypes.create_string_buffer(16)
            bytes_ret = wintypes.DWORD(0)
            ok = self.kernel32.DeviceIoControl(
                self.handle, CONTROL_CODE,
                in_buf, len(in_buf),
                out_buf, 16,
                ctypes.byref(bytes_ret), None
            )
            if not ok:
                return -ctypes.get_last_error()
            raw = struct.unpack('<i', out_buf.raw[:4])[0]
            return raw

    def get_val(self, dev_id: int) -> int:
        res = self._call_method(DSTS, dev_id, 0)
        if res < 0:
            return 0
        return res - 65536

    def set_val(self, dev_id: int, val: int) -> int:
        return self._call_method(DEVS, dev_id, val)

    def get_curve(self, dev_id: int, mode: int = 0) -> Optional[list]:
        with self._lock:
            if not self.handle:
                self.init_driver()
            in_buf = struct.pack('<IIII', DSTS, 8, dev_id, mode)
            out_buf = ctypes.create_string_buffer(32)
            bytes_ret = wintypes.DWORD(0)
            ok = self.kernel32.DeviceIoControl(
                self.handle, CONTROL_CODE,
                in_buf, len(in_buf),
                out_buf, 32,
                ctypes.byref(bytes_ret), None
            )
            if not ok:
                return None
            return list(out_buf.raw[:16])

    def set_curve(self, dev_id: int, curve16: list) -> int:
        if len(curve16) != 16:
            raise ValueError("Curve array must contain exactly 16 bytes")
        with self._lock:
            if not self.handle:
                self.init_driver()
            in_buf = struct.pack('<III', DEVS, 20, dev_id) + bytes(curve16)
            out_buf = ctypes.create_string_buffer(16)
            bytes_ret = wintypes.DWORD(0)
            ok = self.kernel32.DeviceIoControl(
                self.handle, CONTROL_CODE,
                in_buf, len(in_buf),
                out_buf, 16,
                ctypes.byref(bytes_ret), None
            )
            if not ok:
                return -ctypes.get_last_error()
            return struct.unpack('<i', out_buf.raw[:4])[0]

    def get_cpu_rpm(self) -> int:
        val = self.get_val(DEVID_CPU_FAN)
        return max(0, val * 100)

    def get_gpu_rpm(self) -> int:
        val = self.get_val(DEVID_GPU_FAN)
        return max(0, val * 100)

    def get_cpu_temp(self) -> int:
        val = self.get_val(DEVID_CPU_TEMP)
        return max(0, val)

    def get_gpu_temp(self) -> int:
        t = self.get_gpu_temp_nvml()
        if t > 0:
            return t
        val = self.get_val(DEVID_GPU_TEMP)
        return max(0, val)

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "cpu_rpm": self.get_cpu_rpm(),
            "gpu_rpm": self.get_gpu_rpm(),
            "cpu_temp": self.get_cpu_temp(),
            "gpu_temp": self.get_gpu_temp(),
            "mode": self.active_mode,
            "target_percentage": self.target_percentage
        }

    def set_max_speed(self) -> bool:
        self.active_mode = "max"
        self.target_percentage = 100
        cpu_curve = DEFAULT_TEMPS_CPU + [100] * 8
        gpu_curve = DEFAULT_TEMPS_GPU + [100] * 8
        r1 = self.set_curve(DEVID_CPU_FAN_CURVE, cpu_curve)
        r2 = self.set_curve(DEVID_GPU_FAN_CURVE, gpu_curve)
        self.set_val(DEVID_CPU_FAN, 1)
        self.set_val(DEVID_GPU_FAN, 1)
        self.set_windows_active_cooling(True)
        self.start_keepalive()
        return r1 == 1 and r2 == 1

    def set_manual_percentage(self, percentage: int) -> bool:
        percentage = max(20, min(100, int(percentage)))
        self.active_mode = "manual"
        self.target_percentage = percentage

        if percentage >= 95:
            return self.set_max_speed()

        p = percentage
        speeds = [
            max(1, int(p * 0.2)),
            max(5, int(p * 0.35)),
            max(10, int(p * 0.5)),
            max(15, int(p * 0.7)),
            max(20, int(p * 0.85)),
            p, p, min(100, p + 5)
        ]
        r1 = self.set_curve(DEVID_CPU_FAN_CURVE, DEFAULT_TEMPS_CPU + speeds)
        r2 = self.set_curve(DEVID_GPU_FAN_CURVE, DEFAULT_TEMPS_GPU + speeds)
        self.start_keepalive()
        return r1 == 1 and r2 == 1

    def reset_to_auto(self) -> bool:
        self.stop_keepalive()
        self.active_mode = "auto"
        self.target_percentage = None
        r1 = self.set_curve(DEVID_CPU_FAN_CURVE, self.factory_cpu_curve)
        r2 = self.set_curve(DEVID_GPU_FAN_CURVE, self.factory_gpu_curve)
        self.set_val(DEVID_CPU_FAN, 0)
        self.set_val(DEVID_GPU_FAN, 0)
        return r1 == 1 and r2 == 1

    def _keepalive_worker(self):
        while self._keepalive_running:
            time.sleep(3.0)
            if not self._keepalive_running:
                break
            try:
                if self.active_mode == "max":
                    self.set_curve(DEVID_CPU_FAN_CURVE, DEFAULT_TEMPS_CPU + [100] * 8)
                    self.set_curve(DEVID_GPU_FAN_CURVE, DEFAULT_TEMPS_GPU + [100] * 8)
                    self.set_val(DEVID_CPU_FAN, 1)
                    self.set_val(DEVID_GPU_FAN, 1)
                elif self.active_mode == "manual" and self.target_percentage:
                    p = self.target_percentage
                    speeds = [
                        max(1, int(p * 0.2)),
                        max(5, int(p * 0.35)),
                        max(10, int(p * 0.5)),
                        max(15, int(p * 0.7)),
                        max(20, int(p * 0.85)),
                        p, p, min(100, p + 5)
                    ]
                    self.set_curve(DEVID_CPU_FAN_CURVE, DEFAULT_TEMPS_CPU + speeds)
                    self.set_curve(DEVID_GPU_FAN_CURVE, DEFAULT_TEMPS_GPU + speeds)
            except Exception:
                pass

    def start_keepalive(self):
        if not self._keepalive_running:
            self._keepalive_running = True
            self._keepalive_thread = threading.Thread(target=self._keepalive_worker, daemon=True)
            self._keepalive_thread.start()

    def stop_keepalive(self):
        self._keepalive_running = False
        if self._keepalive_thread and self._keepalive_thread.is_alive():
            self._keepalive_thread.join(timeout=1.0)
            self._keepalive_thread = None
