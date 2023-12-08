@echo off
for /f "usebackq tokens=1,* delims==" %%a in ("C:/Users/Wo0zZ1/Desktop/panel/config.cfg") do (
    if "%%a"=="PANELPATH" (
        set "data=%%b"
    )
)
cd /d %data%
python main.py
pause