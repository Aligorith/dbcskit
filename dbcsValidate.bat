@REM Batch script to run dbcsValidate on Windows
@echo off
set path = %PATH%;%CD%\src;

python src\dbcsValidate.py %*

pause

