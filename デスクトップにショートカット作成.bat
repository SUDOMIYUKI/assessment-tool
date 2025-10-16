@echo off
chcp 65001 >nul
echo ========================================
echo デスクトップにショートカットを作成
echo ========================================
echo.

cd /d "%~dp0"

set SCRIPT_DIR=%CD%\
set SHORTCUT_NAME=不登校支援ツール.lnk
set TARGET_PATH=%SCRIPT_DIR%起動.bat
set DESKTOP_PATH=%USERPROFILE%\Desktop

echo 📂 現在のディレクトリ: %SCRIPT_DIR%
echo 🔗 ショートカット名: %SHORTCUT_NAME%
echo 📍 ターゲット: %TARGET_PATH%
echo 💾 デスクトップ: %DESKTOP_PATH%
echo.

REM 一時的なVBScriptファイルを作成してショートカットを作成
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP_PATH%\%SHORTCUT_NAME%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET_PATH%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,21" >> CreateShortcut.vbs
echo oLink.Description = "不登校支援アセスメントツール" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

echo 🔧 ショートカットを作成しています...
cscript //nologo CreateShortcut.vbs

if exist "%DESKTOP_PATH%\%SHORTCUT_NAME%" (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ✅ ショートカットをデスクトップに作成しました！
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 📍 場所: %DESKTOP_PATH%\%SHORTCUT_NAME%
    echo.
    echo 💡 これで、デスクトップのショートカットをダブルクリックするだけで
    echo    アプリを起動できます！
    echo.
    del CreateShortcut.vbs
) else (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ❌ ショートカットの作成に失敗しました
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 💡 手動でショートカットを作成してください:
    echo.
    echo    【方法1】右クリックで作成
    echo    1. 「起動.bat」を右クリック
    echo    2. 「送る」→「デスクトップ（ショートカットを作成）」
    echo.
    echo    【方法2】ドラッグ＆ドロップ
    echo    1. 「起動.bat」を右クリックしながらデスクトップにドラッグ
    echo    2. 「ショートカットをここに作成」を選択
    echo.
    del CreateShortcut.vbs
)

echo.
echo 💡 または、この「起動.bat」ファイル自体をタスクバーに
echo    ピン留めすることもできます！
echo.
pause

