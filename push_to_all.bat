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
    echo ERROR: Failed to push to Hugging Face
    pause
    exit /b 1
) else (
    echo SUCCESS: Pushed to Hugging Face
)

REM Push to GitHub
echo Pushing to GitHub...
git push github main
if errorlevel 1 (
    echo ERROR: Failed to push to GitHub
    pause
    exit /b 1
) else (
    echo SUCCESS: Pushed to GitHub
)

echo ========================================
echo Successfully pushed to both repositories
echo ========================================
pause
