import cx_Freeze
import sys
import os

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["tkinter", "sqlite3", "hashlib", "datetime", "threading", "time", "os", "shutil", "PIL"],
    "excludes": [],
    "include_files": []
}

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

cx_Freeze.setup(
    name="Cacasians Chat Application",
    version="1.0",
    description="Modern Chat Application with Real-time Messaging",
    options={"build_exe": build_exe_options},
    executables=[cx_Freeze.Executable("main.py", base=base, target_name="CacasiansChat.exe")]
)