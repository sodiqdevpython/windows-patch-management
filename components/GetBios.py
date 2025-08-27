import wmi

def get_windows_bios_uuid():
    try:
        c = wmi.WMI()
        for system in c.Win32_ComputerSystemProduct():
            return system.UUID.strip().lower()
    except Exception as e:
        print(f"Error retrieving BIOS UUID: {e}")
        return None
