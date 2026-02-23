@echo off
REM MindBridge Mentor Agent - Quick Commands

if "%1"=="" goto :help
if /i "%1"=="init" goto :init
if /i "%1"=="quiz" goto :quiz
if /i "%1"=="progress" goto :progress
goto :help

:init
echo Initializing MindBridge Mentor Database...
python init_mentor_db.py
goto :end

:quiz
echo Starting Quiz Session...
python quiz_mentor.py
goto :end

:progress
echo Loading Progress Dashboard...
python quiz_mentor.py progress
goto :end

:help
echo.
echo MindBridge Mentor Agent - Command Line Interface
echo ================================================
echo.
echo Commands:
echo   mentor init      - Initialize database (first time only)
echo   mentor quiz      - Start a quiz session
echo   mentor progress  - View learning progress
echo.
echo Example:
echo   mentor quiz
echo.
goto :end

:end
