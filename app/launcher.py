import subprocess
import os


def run_script(script_path):
    if not os.path.exists(script_path):
        return False, f"脚本不存在: {script_path}"
    try:
        if script_path.lower().endswith(".exe"):
            subprocess.Popen([script_path])
        else:
            os.startfile(script_path)
        return True, f"已启动: {script_path}"
    except Exception as e:
        return False, f"启动失败: {e}"


def run_scripts(script_paths):
    results = []
    for path in script_paths:
        ok, msg = run_script(path)
        results.append((ok, msg))
    return results
