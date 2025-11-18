@echo off
echo ================================================================================
echo   FlowPrint - Installation Script
echo ================================================================================
echo.
echo Installing Python dependencies...
echo.

pip install Flask==3.0.0
pip install flask-socketio==5.3.5
pip install python-socketio==5.10.0
pip install python-engineio==4.8.0
pip install Werkzeug==3.0.1

echo.
echo ================================================================================
echo   Installation Complete!
echo ================================================================================
echo.
echo To start FlowPrint, run:
echo   python FlowPrint.py
echo.
echo The web interface will automatically open in your browser.
echo.
pause