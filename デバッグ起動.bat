@echo off
chcp 65001 >nul
title 不登校支援ツール - デバッグ起動
cd /d "%~dp0"

echo ========================================
echo 不登校支援ツール - デバッグ起動
echo ========================================
echo.

echo 現在のディレクトリ: %CD%
echo.

echo Pythonのバージョンを確認中...
python --version
if errorlevel 1 (
    echo エラー: Pythonが見つかりません
    echo.
    echo 解決方法:
    echo 1. Pythonをインストールしてください
    echo 2. PATH環境変数にPythonを追加してください
    echo 3. コマンドプロンプトを再起動してください
    echo.
    pause
    exit /b 1
)

echo.
echo 必要なファイルの存在確認...
if exist "main.py" (
    echo ✓ main.py が見つかりました
) else (
    echo ✗ main.py が見つかりません
)

if exist "requirements.txt" (
    echo ✓ requirements.txt が見つかりました
) else (
    echo ✗ requirements.txt が見つかりません
)

if exist "venv\Scripts\python.exe" (
    echo ✓ 仮想環境が見つかりました
    echo 仮想環境のPythonバージョン:
    "venv\Scripts\python.exe" --version
) else (
    echo ✗ 仮想環境が見つかりません
)

echo.
echo 依存関係を確認中...
if exist "venv\Scripts\python.exe" (
    echo 仮想環境を使用して依存関係を確認...
    "venv\Scripts\python.exe" -c "import tkinter; print('✓ tkinter が利用可能です')"
    "venv\Scripts\python.exe" -c "import sqlite3; print('✓ sqlite3 が利用可能です')"
    "venv\Scripts\python.exe" -c "import openpyxl; print('✓ openpyxl が利用可能です')"
) else (
    echo システムのPythonを使用して依存関係を確認...
    python -c "import tkinter; print('✓ tkinter が利用可能です')"
    python -c "import sqlite3; print('✓ sqlite3 が利用可能です')"
    python -c "import openpyxl; print('✓ openpyxl が利用可能です')"
)

echo.
echo アプリケーションを起動します...
echo ========================================
echo.

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" main.py
) else (
    python main.py
)

echo.
echo ========================================
echo アプリケーションが終了しました。
echo エラーコード: %ERRORLEVEL%
echo ========================================
pause