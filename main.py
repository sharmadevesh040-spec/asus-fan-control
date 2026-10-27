"""
ASUS TUF Fan Speed Controller - Main Entry Point
"""

import sys
import os
import time

# Ensure current directory is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from asus_fan_controller import AsusFanController
import server

def show_interactive_menu():
    ctrl = AsusFanController()
    try:
        while True:
            t = ctrl.get_telemetry()
            print("\n" + "=" * 54)
            print("       ASUS TUF FAN CONTROLLER & MAX RPM BOOSTER")
            print("=" * 54)
            print(f" CPU Fan : {t['cpu_rpm']} RPM  ({t['cpu_temp']}°C)")
            print(f" GPU Fan : {t['gpu_rpm']} RPM  ({t['gpu_temp']}°C)")
            print(f" Mode    : {t['mode'].upper()}")
            print("-" * 54)
            print(" [1] ⚡ Set MAXIMUM Fan Speed (100% Highest RPM)")
            print(" [2] 🌐 Launch Web Dashboard GUI (Browser)")
            print(" [3] 🔄 Restore Factory Automatic Mode (BIOS)")
            print(" [4] 📊 Live Continuous Telemetry Monitor")
            print(" [5] 🎛️  Set Custom Speed Percentage (30% - 100%)")
            print(" [0] ❌ Exit")
            print("-" * 54)

            choice = input("Select an option (0-5): ").strip()

            if choice == "1":
                print("\n[*] Blasting fans to 100% Maximum RPM...")
                ctrl.set_max_speed()
                print("[+] Highest Fan Speed Activated! Fans are ramping up.")
                time.sleep(1.5)
            elif choice == "2":
                print("\n[*] Starting Web Dashboard Server...")
                ctrl.close()
                server.run_server()
                return
            elif choice == "3":
                print("\n[*] Restoring default BIOS automatic fan control...")
                ctrl.reset_to_auto()
                print("[+] Automatic control restored.")
                time.sleep(1.5)
            elif choice == "4":
                print("\n[*] Monitoring live fan RPM & Temps (Press Ctrl+C to return)...")
                try:
                    while True:
                        m = ctrl.get_telemetry()
                        sys.stdout.write(f"\r  CPU: {m['cpu_rpm']:4d} RPM ({m['cpu_temp']:2d}°C) | GPU: {m['gpu_rpm']:4d} RPM ({m['gpu_temp']:2d}°C) | Mode: {m['mode'].upper()}   ")
                        sys.stdout.flush()
                        time.sleep(1.0)
                except KeyboardInterrupt:
                    print("\n[+] Exited monitor.")
            elif choice == "5":
                val = input("\nEnter fan percentage (30 to 100): ").strip()
                try:
                    pct = int(val)
                    if 30 <= pct <= 100:
                        ctrl.set_manual_percentage(pct)
                        print(f"[+] Fan speed set to {pct}%.")
                    else:
                        print("[-] Please enter a value between 30 and 100.")
                except ValueError:
                    print("[-] Invalid number.")
                time.sleep(1.5)
            elif choice in ("0", "q", "exit"):
                print("\nExiting. Fans remain in their current active state.")
                break
            else:
                print("[-] Invalid option. Please choose 0 to 5.")
                time.sleep(1)
    finally:
        ctrl.close()

def main():
    args = sys.argv[1:]
    if not args:
        show_interactive_menu()
        return

    cmd = args[0].lower().strip()
    if cmd in ("gui", "web", "dashboard"):
        server.run_server()
    else:
        # Delegate to asus_fan_controller CLI
        import asus_fan_controller
        asus_fan_controller.main()

if __name__ == "__main__":
    main()
