@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
echo ========================================
echo   Local Model Server - BGE-M3 + Reranker
echo ========================================
echo.

cd /d "%~dp0"

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

:: Install dependencies
echo [1/2] Checking dependencies...
pip show sentence-transformers >nul 2>&1
if %errorlevel% neq 0 (
    echo [INSTALL] Installing dependencies...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies installed
)

echo.
echo [2/2] Starting model server on port 8080...
echo [INFO] First load may take a while, please wait...
echo [INFO] Press Ctrl+C to stop
echo.

python server.py --embedding-path "D:/models/bge-m3" --rerank-path "D:/models/bge-reranker-base" --port 8080 --host 127.0.0.1

pause
