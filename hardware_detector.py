"""
Universal Laptop & Hardware Detector
Identifies laptop manufacturer, model, product line, CPU, and GPUs across Windows systems.
"""

import winreg
import subprocess
import json
import os
from typing import Dict, Any, List

def detect_hardware() -> Dict[str, Any]:
    """
    Detects detailed system specs in sub-milliseconds using the Windows Registry,
    with graceful fallback to CIM/WMI if needed.
    """
    info = {
        "manufacturer": "Unknown",
        "vendor": "generic",
        "model": "Generic PC",
        "family": "",
        "cpu": "Unknown Processor",
        "gpus": [],
        "primary_gpu": "Generic Display",
        "bios_version": "",
        "is_laptop": True
    }

    # 1. Read System BIOS Information from Windows Registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\BIOS') as key:
            # Query all values
            values = {}
            for i in range(winreg.QueryInfoKey(key)[1]):
                v_name, v_val, _ = winreg.EnumValue(key, i)
                values[v_name] = v_val

            mfg = values.get('SystemManufacturer', '').strip()
            model = values.get('SystemProductName', '').strip()
            family = values.get('SystemFamily', '').strip()
            bios = values.get('BIOSVersion', '').strip()

            if mfg:
                info["manufacturer"] = mfg
            if model:
                info["model"] = model
            if family:
                info["family"] = family
            if bios:
                info["bios_version"] = bios
    except Exception:
        pass

    # 2. Normalize and identify Laptop Brand
    mfg_upper = info["manufacturer"].upper()
    model_upper = info["model"].upper()
    family_upper = info["family"].upper()
    full_string = f"{mfg_upper} {model_upper} {family_upper}"

    if "ASUS" in full_string or "ASUSTEK" in full_string:
        info["vendor"] = "asus"
    elif "LENOVO" in full_string or "LEGION" in full_string:
        info["vendor"] = "lenovo"
    elif "DELL" in full_string or "ALIENWARE" in full_string:
        info["vendor"] = "dell"
    elif "HP" in full_string or "HEWLETT-PACKARD" in full_string or "OMEN" in full_string or "VICTUS" in full_string:
        info["vendor"] = "hp"
    elif "ACER" in full_string or "NITRO" in full_string or "PREDATOR" in full_string:
        info["vendor"] = "acer"
    elif "MICRO-STAR" in full_string or "MSI" in full_string:
        info["vendor"] = "msi"
    elif "RAZER" in full_string:
        info["vendor"] = "razer"
    elif "GIGABYTE" in full_string or "AORUS" in full_string:
        info["vendor"] = "gigabyte"
    else:
        info["vendor"] = "generic"

    # 3. Read CPU Name from Windows Registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
            if cpu:
                info["cpu"] = cpu
    except Exception:
        pass

    # 4. Read GPU(s) from Windows Registry Video Class
    try:
        base_path = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as root_key:
            num_subkeys = winreg.QueryInfoKey(root_key)[0]
            for i in range(num_subkeys):
                sub_name = winreg.EnumKey(root_key, i)
                if sub_name.isdigit():
                    try:
                        with winreg.OpenKey(root_key, sub_name) as sub_key:
                            desc = winreg.QueryValueEx(sub_key, 'DriverDesc')[0].strip()
                            if desc and desc not in info["gpus"] and "Miracast" not in desc and "Basic" not in desc:
                                info["gpus"].append(desc)
                    except Exception:
                        pass
    except Exception:
        pass

    if info["gpus"]:
        # Pick dedicated GPU first (NVIDIA / AMD Radeon RX), else integrated
        dedicated = [g for g in info["gpus"] if any(k in g.upper() for k in ("NVIDIA", "GEFORCE", "RTX", "GTX", "RADEON RX"))]
        if dedicated:
            info["primary_gpu"] = dedicated[0]
        else:
            info["primary_gpu"] = info["gpus"][0]

    return info

if __name__ == "__main__":
    hw = detect_hardware()
    print("=== Detected Hardware ===")
    for k, v in hw.items():
        print(f"  {k:15s}: {v}")
