@echo off
chcp 65001 >nul
title 不登校支援ツール - 安全起動
cd /d "%~dp0"

echo ========================================
echo 不登校支援ツール - 安全起動
echo ========================================
echo.

echo ステップ1: 構文チェックを実行中...
python pre_commit_check.py
if errorlevel 1 (
    echo.
    echo ❌ 構文チェックに失敗しました。
    echo 問題を修正してから再実行してください。
    echo.
    pause
    exit /b 1
)

echo.
echo ステップ2: アプリケーションを起動中...
python main.py

if errorlevel 1 (
    echo.
    echo ❌ アプリケーションの起動に失敗しました。
    echo エラーログを確認してください。
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ アプリケーションが正常に起動しました。
echo.
pause

