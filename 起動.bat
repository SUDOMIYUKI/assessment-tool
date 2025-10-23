@echo off
chcp 65001 >nul
title 不登校支援ツール
cd /d "%~dp0"

echo 不登校支援ツールを起動しています...
echo.

REM 仮想環境の確認と起動
if exist "venv\Scripts\python.exe" (
    echo 仮想環境を使用して起動します...
    "venv\Scripts\python.exe" main.py
    if errorlevel 1 (
        echo エラーが発生しました。詳細を確認してください。
        pause
        exit /b 1
    )
) else if exist "python.exe" (
    echo システムのPythonを使用して起動します...
    "python.exe" main.py
    if errorlevel 1 (
        echo エラーが発生しました。詳細を確認してください。
        pause
        exit /b 1
    )
) else (
    echo Pythonが見つかりません。
    echo 以下の方法で起動してください：
    echo 1. Pythonをインストールする
    echo 2. 仮想環境を作成する: python -m venv venv
    echo 3. 仮想環境をアクティベートする: venv\Scripts\activate
    echo 4. 依存関係をインストールする: pip install -r requirements.txt
    echo 5. アプリを起動する: python main.py
    echo.
    pause
    exit /b 1
)

echo.
echo アプリを起動しました！
echo.
pause
