@echo off
chcp 65001 >nul
title 不登校支援ツール - デバッグモード
color 0A
echo ========================================
echo デバッグモード - 詳細情報を表示
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 📂 現在のディレクトリ
echo %CD%
echo.

echo [2/5] 📋 必要なファイルの確認
echo.
if exist "main.py" (
    echo ✅ main.py が見つかりました
) else (
    echo ❌ main.py が見つかりません
)

if exist "venv" (
    echo ✅ venv フォルダが見つかりました
) else (
    echo ❌ venv フォルダが見つかりません
)

if exist "venv\Scripts\python.exe" (
    echo ✅ venv\Scripts\python.exe が見つかりました
) else (
    echo ❌ venv\Scripts\python.exe が見つかりません
)

if exist "requirements.txt" (
    echo ✅ requirements.txt が見つかりました
) else (
    echo ❌ requirements.txt が見つかりません
)
echo.

echo [3/5] 🐍 Pythonのバージョン確認
venv\Scripts\python.exe --version 2>nul
if errorlevel 1 (
    echo ❌ Pythonの実行に失敗しました
    echo.
    echo 💡 以下のコマンドで仮想環境を再作成してください:
    echo    python -m venv venv
    echo    venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo.

echo [4/5] 📦 インストール済みパッケージ
venv\Scripts\pip.exe list 2>nul | findstr /i "anthropic openpyxl pykakasi"
echo.

echo [5/5] 🚀 アプリケーションを起動します
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 💡 このウィンドウを閉じないでください！
echo    アプリを閉じるまで、このウィンドウで
echo    エラーメッセージなどを確認できます。
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause

echo.
echo [起動中] アプリを起動しています...
echo.

venv\Scripts\python.exe main.py

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo アプリが終了しました
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if errorlevel 1 (
    echo ❌ エラーが発生しました
    echo.
    echo 上記のエラーメッセージを確認してください。
    echo.
) else (
    echo ✅ 正常に終了しました
    echo.
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 💡 よくあるエラーと解決方法
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 【エラー1】ModuleNotFoundError
echo → 解決方法: venv\Scripts\pip.exe install -r requirements.txt
echo.
echo 【エラー2】データベースエラー
echo → 解決方法: Documents\不登校支援ツール\data\records.db を削除
echo.
echo 【エラー3】APIキーエラー
echo → 解決方法: config.py のAPIキーを確認
echo.
pause

