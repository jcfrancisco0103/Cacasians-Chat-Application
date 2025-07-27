@echo off
echo ========================================
echo    Building Cacasians Chat Executable
echo ========================================
echo.

echo Installing cx_Freeze if not already installed...
pip install cx_Freeze

echo.
echo Building executable file...
python setup.py build

echo.
echo Build complete! Check the 'build' folder for your executable.
echo The executable will be named 'CacasiansChat.exe'
echo.

pause