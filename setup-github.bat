@echo off
chcp 65001 >nul
cls
echo ====================================================
echo   GitHub Repository Setup Helper
echo ====================================================
echo.
echo This script will help you push your code to GitHub
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✓ Git is installed

REM Check if already initialized
if exist .git (
    echo ✓ Git repository already initialized
) else (
    echo Initializing git repository...
    git init
    echo ✓ Repository initialized
)

echo.
echo ====================================================
echo Step 1: Configure Git User
echo ====================================================
echo.
set /p git_name="Enter your GitHub username: "
set /p git_email="Enter your GitHub email: "

git config user.name "%git_name%"
git config user.email "%git_email%"
echo ✓ Git user configured

echo.
echo ====================================================
echo Step 2: Add Files to Git
echo ====================================================
echo.
echo Adding all files to git...
git add .
echo ✓ Files added

echo.
echo ====================================================
echo Step 3: Commit Changes
echo ====================================================
echo.
git commit -m "Initial commit: AI Chat Platform with sleep/wake backend"
echo ✓ Changes committed

echo.
echo ====================================================
echo Step 4: Connect to GitHub Repository
echo ====================================================
echo.
echo IMPORTANT: Create a GitHub repository first!
echo.
echo 1. Go to https://github.com/new
echo 2. Repository name: ai-chat-platform
echo 3. Set to Public or Private
echo 4. Do NOT initialize with README
echo 5. Click "Create repository"
echo.
pause

echo.
set /p github_username="Enter your GitHub username: "
set /p repo_name="Enter repository name (e.g., ai-chat-platform): "

git remote remove origin 2>nul
git remote add origin https://github.com/%github_username%/%repo_name%.git
echo ✓ Remote repository connected

echo.
echo ====================================================
echo Step 5: Push to GitHub
echo ====================================================
echo.
echo Pushing to GitHub...
echo You may be prompted for your GitHub credentials or personal access token
echo.
git push -u origin main 2>nul || git push -u origin master
echo.
echo ✓ Code pushed to GitHub!
echo.
echo ====================================================
echo DEPLOYMENT URLs
echo ====================================================
echo.
echo GitHub Repository: https://github.com/%github_username%/%repo_name%
echo.
echo Next steps:
echo 1. Deploy backend to Hugging Face Spaces
echo 2. Deploy frontend to Cloudflare Pages
echo 3. Configure Firebase
echo.
echo See DEPLOYMENT_GUIDE.md for detailed instructions
echo.
pause