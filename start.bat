@echo off
call .\venv\Scripts\activate.bat
call python run.py --execution-provider cuda --frame-processor face_swapper face_enhancer
pause
