@echo off
echo ========================================
echo    Cacasians Chat Application Setup
echo ========================================
echo.

echo Installing required dependencies...
pip install Pillow==10.0.1
pip install cx_Freeze

echo.
echo Dependencies installed successfully!
echo.

echo Starting Cacasians Chat Application...
python enhanced_main.py

pause