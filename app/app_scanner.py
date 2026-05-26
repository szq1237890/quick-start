import os
import winreg
import re


def scan_installed_apps():
    apps = []
    seen = set()
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, path in registry_paths:
        try:
            key = winreg.OpenKey(hive, path)
        except OSError:
            continue
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                name = _get_value(subkey, "DisplayName")
                if not name:
                    winreg.CloseKey(subkey)
                    i += 1
                    continue

                exe = _find_exe_from_registry(subkey, name)
                if exe and name not in seen:
                    seen.add(name)
                    apps.append({"name": name, "exe": exe})

                winreg.CloseKey(subkey)
                i += 1
            except OSError:
                break
            except Exception:
                i += 1
                continue
        winreg.CloseKey(key)
    apps.sort(key=lambda x: x["name"].lower())
    return apps


def _find_exe_from_registry(subkey, name):
    """Try multiple registry fields to find the executable."""
    # 1. Try InstallLocation
    install_loc = _get_value(subkey, "InstallLocation")
    if install_loc and isinstance(install_loc, str):
        install_loc = _clean_path(install_loc)
        if os.path.isfile(install_loc) and install_loc.lower().endswith(".exe"):
            return install_loc
        if os.path.isdir(install_loc):
            exe = _find_exe_in_dir(install_loc, name)
            if exe:
                return exe

    # 2. Try DisplayIcon
    display_icon = _get_value(subkey, "DisplayIcon", "")
    if display_icon and isinstance(display_icon, str):
        icon_path = _extract_path_from_icon(display_icon)
        if icon_path and os.path.isfile(icon_path) and icon_path.lower().endswith(".exe"):
            return icon_path

    # 3. Try UninstallString
    uninstall_str = _get_value(subkey, "UninstallString", "")
    if uninstall_str and isinstance(uninstall_str, str):
        exe_path = _extract_exe_from_string(uninstall_str)
        if exe_path and os.path.isfile(exe_path):
            return exe_path

    # 4. Try QuietUninstallString
    quiet_uninstall = _get_value(subkey, "QuietUninstallString", "")
    if quiet_uninstall and isinstance(quiet_uninstall, str):
        exe_path = _extract_exe_from_string(quiet_uninstall)
        if exe_path and os.path.isfile(exe_path):
            return exe_path

    # 5. Try ModifyPath
    modify_path = _get_value(subkey, "ModifyPath", "")
    if modify_path and isinstance(modify_path, str):
        exe_path = _extract_exe_from_string(modify_path)
        if exe_path and os.path.isfile(exe_path):
            return exe_path

    return None


def _clean_path(path):
    """Remove quotes and trailing backslashes."""
    path = path.strip().strip('"').strip("'")
    if path.endswith(os.sep):
        path = path[:-1]
    return path


def _extract_path_from_icon(icon_str):
    """Extract exe path from DisplayIcon format (path,index)."""
    icon_str = _clean_path(icon_str)
    # Remove index after comma: "C:\path\app.exe,0" -> "C:\path\app.exe"
    if "," in icon_str:
        icon_str = icon_str.rsplit(",", 1)[0]
    return icon_str if icon_str.lower().endswith(".exe") else None


def _extract_exe_from_string(s):
    """Extract exe path from uninstall/modify command string."""
    s = s.strip()
    # Handle quoted paths: '"C:\Program Files\App\uninstall.exe" /arg'
    match = re.match(r'^"([^"]+\.exe)"', s, re.IGNORECASE)
    if match:
        return _clean_path(match.group(1))
    # Handle unquoted paths: 'C:\Program Files\App\uninstall.exe /arg'
    match = re.match(r'^([^\s]+\.exe)', s, re.IGNORECASE)
    if match:
        return _clean_path(match.group(1))
    # Try to find any exe in the string
    match = re.search(r'([A-Za-z]:[^\s"]*\.exe)', s, re.IGNORECASE)
    if match:
        return _clean_path(match.group(1))
    return None


def _get_value(key, name, default=None):
    try:
        val, _ = winreg.QueryValueEx(key, name)
        return val if val else default
    except Exception:
        return default


def _find_exe_in_dir(dir_path, app_name=None):
    """Find exe in directory, preferring exe with matching name."""
    try:
        exes = [f for f in os.listdir(dir_path) if f.lower().endswith(".exe")]
        if not exes:
            return None
        # If app_name provided, try to find matching exe
        if app_name:
            app_name_lower = app_name.lower()
            for exe in exes:
                if app_name_lower in exe.lower():
                    return os.path.join(dir_path, exe)
        # Return first exe found
        return os.path.join(dir_path, exes[0])
    except OSError:
        return None
