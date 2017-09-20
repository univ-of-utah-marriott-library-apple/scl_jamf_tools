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
    script="cargo_ship.py",
    base="Win32GUI",
    icon="cargo_ship.ico"
    )
setup(  name = "Cargo Ship",
        version = "1.0.1",
        description = "Put your stuff into JAMF!",
#       options = {"build_exe": build_exe_options},
        executables = [Executable("cargo_ship.py", base=base)])
