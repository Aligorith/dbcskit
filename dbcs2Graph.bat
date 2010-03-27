@REM Batch script to run dbcs2Graph on Windows
@echo off
set path = %PATH%;%CD%\src;

python src\dbcs2Graph.py %*

pause

