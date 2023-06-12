@echo off
call .\venv\Scripts\activate.bat
call python run.py --gpu-vendor nvidia
pause
