@echo off
setlocal
for %%A in ("%~dp0.") do set p=%%~dpA
call python %p%rbr.py %*
endlocal
