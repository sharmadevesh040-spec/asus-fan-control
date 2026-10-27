"""
Universal Cross-Laptop Fan Speed Controller (Compatible with AsusFanController API)
Automatically detects your laptop (ASUS, Lenovo, Dell, HP, Acer, MSI, etc.)
and engages the correct hardware driver.
"""

import sys
import os
import time

from universal_controller import UniversalFanController

# Alias for backwards compatibility
AsusFanController = UniversalFanController

def main():
    ctrl = UniversalFanController()
    info = ctrl.get_info()
    hw = info["hardware"]
    args = sys.argv[1:]

    if not args:
        print("\n=== Universal Cross-Laptop Fan Controller ===")
        print(f"  Laptop Detected : {hw['manufacturer']} - {hw['model']}")
        print(f"  Hardware Engine : {info['backend']} ({ctrl.vendor.upper()})")
        print(f"  Processor       : {hw['cpu']}")
        print(f"  Graphics        : {hw['primary_gpu']}")
        print("\nUsage:")
        print("  python asus_fan_controller.py max       - Force HIGHEST / 100% Maximum Fan RPM")
        print("  python asus_fan_controller.py auto      - Reset to factory default automatic BIOS mode")
        print("  python asus_fan_controller.py <30-100>  - Set manual fan percentage (e.g. 80)")
        print("  python asus_fan_controller.py turbo     - Set Turbo preset (85%)")
        print("  python asus_fan_controller.py balanced  - Set Balanced preset (50%)")
        print("  python asus_fan_controller.py silent    - Set Quiet preset (30%)")
        print("  python asus_fan_controller.py status    - Show live fan speeds & temperatures")
        print("  python asus_fan_controller.py monitor   - Live real-time terminal monitoring")
        print("")
        t = ctrl.get_telemetry()
        print(f"Current Status: CPU Fan={t['cpu_rpm']} RPM ({t['cpu_temp']}°C) | GPU Fan={t['gpu_rpm']} RPM ({t['gpu_temp']}°C) | Mode={t['mode']}")
        ctrl.close()
        return

    cmd = args[0].lower().strip()
    if cmd in ("status", "info"):
        t = ctrl.get_telemetry()
        print("\n--- Live Hardware Telemetry ---")
        print(f"  Laptop        : {hw['manufacturer']} - {hw['model']}")
        print(f"  Hardware      : {hw['cpu']} | {hw['primary_gpu']}")
        print(f"  Active Engine : {info['backend']}")
        print(f"  CPU Fan Speed : {t['cpu_rpm']} RPM")
        print(f"  GPU Fan Speed : {t['gpu_rpm']} RPM")
        print(f"  CPU Temp      : {t['cpu_temp']} °C")
        print(f"  GPU Temp      : {t['gpu_temp']} °C")
        print(f"  Fan Mode      : {t['mode'].upper()}")
        if t.get('target_percentage'):
            print(f"  Target Speed  : {t['target_percentage']}%")
        print("-------------------------------\n")
    elif cmd in ("monitor", "watch"):
        print(f"Monitoring Fan Speeds on {hw['model']} (Press Ctrl+C to stop)...")
        try:
            while True:
                t = ctrl.get_telemetry()
                sys.stdout.write(f"\r[Telemetry] CPU: {t['cpu_rpm']:4d} RPM ({t['cpu_temp']:2d}°C) | GPU: {t['gpu_rpm']:4d} RPM ({t['gpu_temp']:2d}°C) | Mode: {t['mode'].upper()}   ")
                sys.stdout.flush()
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nStopped.")
    elif cmd in ("max", "highest", "full", "overboost", "100"):
        print(f"[*] Activating MAXIMUM HIGHEST FAN SPEED for {hw['model']}...")
        if ctrl.set_max_speed():
            print("[+] Success: Fans set to 100% Maximum Speed.")
            print("[*] Monitoring fan ramp-up...")
            for i in range(1, 6):
                time.sleep(1)
                t = ctrl.get_telemetry()
                print(f"    T+{i:02d}s: CPU={t['cpu_rpm']} RPM ({t['cpu_temp']}°C), GPU={t['gpu_rpm']} RPM ({t['gpu_temp']}°C)")
            print("\n[+] Highest fan speed active! Use dashboard or 'auto' command to restore.")
        else:
            print("[-] Failed to apply max speed.")
    elif cmd in ("auto", "reset", "bios", "default"):
        print("[*] Restoring default factory BIOS fan curve...")
        if ctrl.reset_to_auto():
            print("[+] Success: Restored to Automatic Factory Mode.")
        else:
            print("[-] Failed to restore default curve.")
    else:
        if ctrl.set_preset(cmd):
            print(f"[+] Fan speed mode applied: {cmd}")
            t = ctrl.get_telemetry()
            print(f"    Current: CPU={t['cpu_rpm']} RPM, GPU={t['gpu_rpm']} RPM")
        else:
            print(f"[-] Unknown command or invalid percentage: {cmd}")

    ctrl.close()

if __name__ == "__main__":
    main()
