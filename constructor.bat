@rem #################################################################
@rem 
@rem 				Do not Change this Script!
@rem		Constructor batch Script for windows - By (C)McCDcardMaster
@rem 
@rem #################################################################
@echo off
setlocal
for /f "tokens=1* delims==" %%a in ('findstr /B "constructorUtilVersion=" constructor\wrapper\constructor-wrapper.properties') do set "version=%%~b"
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed on your computer.
    echo Please download and install Python from the following link:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
set PYTHON=python
set WRAPPER_SCRIPT=constructor\wrapper\constructor-wrapper.pyc
set TASK_SCRIPT=constructor\%version%\ConstructorTasksScript.pyc

%PYTHON% %WRAPPER_SCRIPT%
if %errorlevel% neq 0 (
    echo Execution of %WRAPPER_SCRIPT% failed.
    pause
    exit /b 1
)

:execute_task_script
%PYTHON% %TASK_SCRIPT% %*
endlocal