@echo off


if not defined PYTHON (set PYTHON=py)



REM Set up Python environment
set PYTHON_ENV=%cd%\venv
if not exist %PYTHON_ENV%\Scripts\activate.bat (
    python -m venv %PYTHON_ENV%
)

REM Activate Python environment
call %PYTHON_ENV%\Scripts\activate.bat

REM Install dependencies
python -m pip install -r requirements.txt

REM Leave command prompt open
cmd.exe /k "echo Python environment activated. Run your script now. & echo To deactivate the environment, type 'deactivate' and press Enter."

REM Deactivate Python environment
deactivate

