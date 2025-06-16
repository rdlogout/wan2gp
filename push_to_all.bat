@echo off
REM Batch file to push to both Hugging Face and GitHub repositories
REM Usage: push_to_all.bat [commit_message]

echo ========================================
echo Pushing to both Hugging Face and GitHub
echo ========================================

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not in a git repository
    pause
    exit /b 1
)

REM Clean up cache files that might cause issues
echo Cleaning up cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Check if there are any changes to commit
git diff-index --quiet HEAD --
if errorlevel 1 (
    REM There are changes to commit
    if "%~1"=="" (
        set /p COMMIT_MSG="Enter commit message: "
    ) else (
        set COMMIT_MSG=%~1
    )
    
    echo Adding and committing changes...
    git add .
    git commit -m "!COMMIT_MSG!"
    if errorlevel 1 (
        echo ERROR: Failed to commit changes
        pause
        exit /b 1
    )
) else (
    echo No changes to commit. Pushing existing commits...
)

REM Push to Hugging Face (origin)
echo Pushing to Hugging Face...
git push origin main
if errorlevel 1 (
    echo WARNING: Failed to push to Hugging Face
    echo This might be due to binary files or other restrictions
    set HF_SUCCESS=false
) else (
    echo SUCCESS: Pushed to Hugging Face
    set HF_SUCCESS=true
)

REM Push to GitHub
echo Pushing to GitHub...
git push github main
if errorlevel 1 (
    echo ERROR: Failed to push to GitHub
    set GH_SUCCESS=false
) else (
    echo SUCCESS: Pushed to GitHub
    set GH_SUCCESS=true
)

echo ========================================
if "%HF_SUCCESS%"=="true" if "%GH_SUCCESS%"=="true" (
    echo Successfully pushed to both repositories
) else (
    echo Check the output above for any failed pushes
)
echo ========================================
pause
