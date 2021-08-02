import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
packages = []
files = ["data", "startup.json"]
build_exe_options = {"excludes": ["PyQt4.QtSql", "sqlite3",
                     "scipy.lib.lapack.flapack",
                     "PyQt4.QtNetwork",
                     "PyQt4.QtScript",
                     "numpy.core._dotblas",
                     "PyQt5"], "include_files": files, "optimize": 2, "packages": packages}
# GUI applications require a different base on Windows (the default is for
# a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Symulator Bombermana 2D",
      version="0.1",
      description="release",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base)])
