@echo off
call .\venv\Scripts\activate.bat
call python run.py --gpu_vendor nvidia
pause
