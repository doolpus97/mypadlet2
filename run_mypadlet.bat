@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [1/2] 가상환경을 만들고 있습니다...
  py -m venv .venv
  if errorlevel 1 goto :error
  echo [2/2] 필요한 패키지를 설치합니다...
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :error
)
if "%MYPADLET_TEACHER_PIN%"=="" set MYPADLET_TEACHER_PIN=2468
if "%MYPADLET_DATA_DIR%"=="" set MYPADLET_DATA_DIR=D:\MyPadlet
.venv\Scripts\python.exe app.py
if errorlevel 1 goto :error
goto :eof
:error
echo.
echo 실행 중 오류가 발생했습니다.
pause
