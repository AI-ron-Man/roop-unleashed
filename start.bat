@echo off
call .\venv\Scripts\activate.bat
call python run.py --execution-provider cuda
pause
