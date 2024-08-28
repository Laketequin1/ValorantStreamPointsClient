import winreg

def set_mouse_sensitivity_registry(sensitivity):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Mouse", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "MouseSensitivity", 0, winreg.REG_SZ, str(sensitivity))
    winreg.CloseKey(key)

# Set sensitivity to a lower value (valid range is 1 to 20)
new_sensitivity = 10
set_mouse_sensitivity_registry(new_sensitivity)
