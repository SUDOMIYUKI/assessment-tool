@echo off
chcp 65001 >nul
title 不登校支援ツール
echo ========================================
echo 不登校支援ツール 起動中...
echo ========================================
echo.

cd /d "%~dp0"
echo 📂 現在のディレクトリ: %CD%
echo 📂 このディレクトリにあるファイル:
dir /b main.py venv 2>nul
echo.

REM 仮想環境のチェック
if not exist "venv\Scripts\python.exe" (
    echo ❌ [エラー] 仮想環境が見つかりません
    echo.
    echo 📋 初回セットアップが必要です。以下のコマンドを実行してください:
    echo.
    echo    python -m venv venv
    echo    venv\Scripts\pip.exe install -r requirements.txt
    echo.
    echo または、以下のコマンドをコピーして実行:
    echo.
    echo python -m venv venv ^&^& venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ 仮想環境を確認しました
echo 🚀 アプリケーションを起動しています...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 アプリのウィンドウが表示されたら、このウィンドウは
echo    そのままにしておいてください。
echo    アプリを閉じると、このウィンドウも自動的に閉じます。
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo [起動中] Pythonを実行しています...
echo.

venv\Scripts\python.exe main.py

set APP_EXIT_CODE=%errorlevel%
echo.
echo [終了] アプリが終了しました (終了コード: %APP_EXIT_CODE%)
echo.

if %APP_EXIT_CODE% neq 0 (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ❌ [エラー] アプリがエラーで終了しました
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo 📋 エラーの詳細は上記のメッセージを確認してください
    echo.
    echo 💡 次回起動時は以下のコマンドを直接実行してください:
    echo.
    echo    venv\Scripts\python.exe main.py
    echo.
    echo 📞 トラブルシューティング:
    echo    - 依存パッケージの再インストール:
    echo      venv\Scripts\pip.exe install -r requirements.txt
    echo.
    echo    - データベースのリセット:
    echo      Documents\不登校支援ツール\data\records.db を削除
    echo.
) else (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo ✅ アプリケーションが正常に終了しました
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
)

echo.
echo 💡 今後は以下の方法でも起動できます:
echo.
echo    方法1: 起動.bat をダブルクリック
echo    方法2: コマンドプロンプトで: venv\Scripts\python.exe main.py
echo    方法3: PowerShellで: venv\Scripts\python.exe main.py
echo.
pause
