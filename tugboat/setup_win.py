import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

target = Executable(
    script="tugboat",
    base="Win32GUI",
    icon="tugboat_icon.ico"
    )
setup(  name = "Tugboat",
        version = "1.5.2",
        description = "Put your stuff into JAMF!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("tugboat_pc.py", base=base)])
