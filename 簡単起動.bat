@echo off
title 不登校支援ツール - 簡単起動
cd /d "%~dp0"
start "" venv\Scripts\python.exe main.py
echo.
echo アプリを起動しました！
echo.
echo このウィンドウは閉じても大丈夫です。
echo アプリのウィンドウが表示されるまでお待ちください。
echo.
timeout /t 3 /nobreak >nul
exit

