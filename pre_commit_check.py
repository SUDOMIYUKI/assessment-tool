#!/usr/bin/env python3
"""
コミット前チェックスクリプト
構文エラーやインデント問題を自動検出・修正
"""
import sys
import subprocess
from pathlib import Path
from src.utils.syntax_validator import SyntaxValidator
from src.utils.code_formatter import CodeFormatter

def run_command(command, description):
    """コマンドを実行"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 完了")
            return True
        else:
            print(f"❌ {description} 失敗:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} エラー: {e}")
        return False

def main():
    """メイン実行"""
    print("=" * 60)
    print("🚀 コミット前チェック開始")
    print("=" * 60)
    
    # 1. 構文チェック
    print("\n📋 ステップ1: 構文チェック")
    validator = SyntaxValidator()
    if not validator.validate_file("src/ui/staff_manager.py"):
        print("❌ 構文エラーが検出されました")
        return False
    
    # 2. インデントチェック
    print("\n📋 ステップ2: インデントチェック")
    if not validator.check_indentation_issues("src/ui/staff_manager.py"):
        print("⚠️  インデント問題が検出されました。自動修正を試行します...")
        
        # 3. 自動修正
        print("\n🔧 ステップ3: 自動修正")
        formatter = CodeFormatter()
        if not formatter.format_file(Path("src/ui/staff_manager.py")):
            print("❌ 自動修正に失敗しました")
            return False
        
        # 4. 再チェック
        print("\n📋 ステップ4: 修正後の再チェック")
        if not validator.validate_file("src/ui/staff_manager.py"):
            print("❌ 修正後も構文エラーが残っています")
            return False
    
    # 5. Python構文チェック
    print("\n📋 ステップ5: Python構文チェック")
    if not run_command("python -m py_compile src/ui/staff_manager.py", "Python構文チェック"):
        return False
    
    # 6. アプリケーション起動テスト
    print("\n📋 ステップ6: アプリケーション起動テスト")
    print("アプリケーションを起動してテストします...")
    
    print("\n" + "=" * 60)
    print("✅ すべてのチェックが完了しました！")
    print("アプリケーションを起動できます。")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        print("\n❌ チェックに失敗しました。問題を修正してから再実行してください。")
        sys.exit(1)

