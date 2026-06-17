@echo off
title HACA GPT 2.0 — Starting...
color 0A

echo.
echo  ██╗  ██╗ █████╗  ██████╗ █████╗      ██████╗ ██████╗ ████████╗
echo  ██║  ██║██╔══██╗██╔════╝██╔══██╗    ██╔════╝ ██╔══██╗╚══██╔══╝
echo  ███████║███████║██║     ███████║    ██║  ███╗██████╔╝   ██║   
echo  ██╔══██║██╔══██║██║     ██╔══██║    ██║   ██║██╔═══╝    ██║   
echo  ██║  ██║██║  ██║╚██████╗██║  ██║    ╚██████╔╝██║        ██║   
echo  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝        ╚═╝   
echo.
echo  AI-Powered Educational Chatbot
echo  ================================================
echo.

:: Detect Python command
set PYTHON=
for %%P in (py python3 python) do (
    if not defined PYTHON (
        %%P --version >nul 2>&1 && set PYTHON=%%P
    )
)

if not defined PYTHON (
    echo  [ERROR] Python not found!
    echo.
    echo  Please install Python from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo  [OK] Using Python: %PYTHON%
echo.

:: Change to the gpt directory
cd /d "%~dp0"

:: Check for required packages and install if missing
echo  [CHECK] Verifying dependencies...
%PYTHON% -c "import flask" 2>nul || (
    echo  [INSTALL] Installing Flask...
    %PYTHON% -m pip install flask flask-cors --quiet
)
%PYTHON% -c "import chromadb" 2>nul || (
    echo  [INSTALL] Installing chromadb...
    %PYTHON% -m pip install chromadb --quiet
)
%PYTHON% -c "import sentence_transformers" 2>nul || (
    echo  [INSTALL] Installing sentence-transformers...
    %PYTHON% -m pip install sentence-transformers --quiet
)
%PYTHON% -c "import tiktoken" 2>nul || (
    echo  [INSTALL] Installing tiktoken...
    %PYTHON% -m pip install tiktoken --quiet
)
%PYTHON% -c "import openai" 2>nul || (
    echo  [INSTALL] Installing openai...
    %PYTHON% -m pip install openai --quiet
)
%PYTHON% -c "import dotenv" 2>nul || (
    echo  [INSTALL] Installing python-dotenv...
    %PYTHON% -m pip install python-dotenv --quiet
)

echo  [OK] All dependencies ready!
echo.
echo  ================================================
echo   Starting HACA GPT server on http://localhost:5000
echo   Press Ctrl+C to stop the server
echo  ================================================
echo.

:: Launch the Flask server
%PYTHON% server.py

echo.
echo  Server stopped.
pause
