@echo off
chcp 65001 >nul
title 不登校支援ツール - 簡単起動
cd /d "%~dp0"

echo 不登校支援ツールを起動しています...
echo.

REM 現在のディレクトリを確認
echo 現在のディレクトリ: %CD%
echo.

REM Pythonの存在確認
python --version >nul 2>&1
if errorlevel 1 (
    echo Pythonが見つかりません。Pythonをインストールしてください。
    echo https://www.python.org/downloads/ からダウンロードできます。
    pause
    exit /b 1
)

REM 仮想環境の確認
if exist "venv\Scripts\python.exe" (
    echo 仮想環境が見つかりました。
    echo 仮想環境をアクティベートして起動します...
    call "venv\Scripts\activate.bat"
    python main.py
) else (
    echo 仮想環境が見つかりません。
    echo システムのPythonを使用して起動します...
    python main.py
)

if errorlevel 1 (
    echo.
    echo エラーが発生しました。
    echo 詳細なエラーメッセージを確認してください。
    echo.
    pause
) else (
    echo.
    echo アプリケーションが正常に終了しました。
    echo.
    pause
)

