@echo off
REM evrmem - QMD CLI 快捷命令 (Windows)
REM 用法: evrmem add/search/rag/query/stats

setlocal enabledelayedexpansion

REM 设置离线模式，避免网络探测
set "EVREM_HOME=%USERPROFILE%\.evrmem"
set "HF_HUB_OFFLINE=1"
set "TRANSFORMERS_OFFLINE=1"

REM 查找 Python
set "PYTHON="
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 set "PYTHON=python"
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 set "PYTHON=py"
where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 set "PYTHON=python3"

if "%PYTHON%"=="" (
    echo [ERROR] 未找到 Python，请安装 Python 3.9+
    exit /b 1
)

REM 解析参数
set "CMD=%~1"
set "REST=%~2"

if "%CMD%"=="" (
    "%PYTHON%" -m qmd
) else if "%CMD%"=="-v" (
    "%PYTHON%" -m qmd --version
) else if "%CMD%"=="--version" (
    "%PYTHON%" -m qmd --version
) else (
    "%PYTHON%" -m qmd %*
)
