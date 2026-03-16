@echo off
chcp 65001 >nul
echo ========================================
echo   Mahle 批次查詢 - 上傳到 GitHub
echo ========================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Git，請先安裝：
    echo   https://git-scm.com/download/win
    echo.
    echo 安裝完成後，請重新開啟此腳本。
    pause
    exit /b 1
)

cd /d "%~dp0"

if not exist ".git" (
    echo 正在初始化 Git 倉庫...
    git init
    git branch -M main
)

echo.
echo 加入檔案...
git add .

echo.
echo 檢查狀態...
git status

echo.
set /p COMMIT_MSG="輸入 commit 訊息 (直接 Enter 使用預設): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit: Mahle 批次查詢網頁版

git add .
git commit -m "%COMMIT_MSG%" 2>nul
if errorlevel 1 (
    echo.
    echo 無新變更或已提交完成。
)

echo.
echo ----------------------------------------
echo 下一步：在 GitHub 建立倉庫並設定 remote
echo ----------------------------------------
echo.
echo 1. 開啟 https://github.com/new
echo 2. 倉庫名稱：MahlePartNumberSearch (或自訂)
echo 3. 選擇 Public
echo 4. 「不要」勾選 Initialize with README
echo 5. 點 Create repository
echo.
set /p REPO_URL="請貼上您的 GitHub 倉庫 URL (例: https://github.com/您的帳號/MahlePartNumberSearch.git): "

if "%REPO_URL%"=="" (
    echo 未輸入 URL，跳過 remote 設定。
    echo 您之後可手動執行：
    echo   git remote add origin 您的倉庫URL
    echo   git push -u origin main
) else (
    git remote remove origin 2>nul
    git remote add origin "%REPO_URL%"
    echo.
    echo 正在推送到 GitHub...
    git push -u origin main
    if errorlevel 1 (
        echo.
        echo [提示] 若出現認證錯誤，請使用：
        echo   - GitHub Desktop 或
        echo   - Personal Access Token 作為密碼
    ) else (
        echo.
        echo 上傳完成！
    )
)

echo.
pause
