"""
構文チェックとバリデーション機能
"""
import ast
import sys
from pathlib import Path

class SyntaxValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path):
        """ファイルの構文をチェック"""
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 構文チェック
            try:
                ast.parse(content)
                print(f"✅ {file_path} の構文チェック: OK")
                return True
            except SyntaxError as e:
                error_msg = f"❌ 構文エラー: {file_path}:{e.lineno}: {e.msg}"
                print(error_msg)
                self.errors.append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"❌ ファイル読み込みエラー: {file_path}: {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
    
    def check_indentation_issues(self, file_path):
        """インデント問題をチェック"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            issues = []
            for i, line in enumerate(lines, 1):
                # 空行やコメント行はスキップ
                if not line.strip() or line.strip().startswith('#'):
                    continue
                
                # tryブロックの後の行のインデントをチェック
                if line.strip().startswith('try:'):
                    # 次の行のインデントをチェック
                    if i < len(lines):
                        next_line = lines[i]
                        if next_line.strip() and not next_line.startswith('    '):
                            issues.append(f"行 {i+1}: tryブロック内のインデントが正しくありません")
                
                # for文やif文がtryブロックの外に出ていないかチェック
                if (line.strip().startswith('for ') or line.strip().startswith('if ')) and not line.startswith('    '):
                    # 前の行がtry:で終わっている場合
                    if i > 1 and lines[i-2].strip().endswith('try:'):
                        issues.append(f"行 {i}: {line.strip()[:20]}... がtryブロックの外に出ています")
            
            if issues:
                for issue in issues:
                    print(f"⚠️  {issue}")
                    self.warnings.append(issue)
                return False
            else:
                print(f"✅ {file_path} のインデントチェック: OK")
                return True
                
        except Exception as e:
            print(f"❌ インデントチェックエラー: {e}")
            return False
    
    def validate_all_python_files(self, directory):
        """ディレクトリ内のすべてのPythonファイルをチェック"""
        python_files = list(Path(directory).rglob("*.py"))
        all_valid = True
        
        print(f"🔍 {len(python_files)}個のPythonファイルをチェック中...")
        
        for file_path in python_files:
            if not self.validate_file(file_path):
                all_valid = False
            
            if not self.check_indentation_issues(file_path):
                all_valid = False
        
        return all_valid

def main():
    """メイン実行"""
    validator = SyntaxValidator()
    
    # 現在のディレクトリのPythonファイルをチェック
    current_dir = Path.cwd()
    
    print("=" * 50)
    print("構文チェックとバリデーション開始")
    print("=" * 50)
    
    if validator.validate_all_python_files(current_dir):
        print("\n✅ すべてのファイルが正常です")
        sys.exit(0)
    else:
        print("\n❌ エラーが見つかりました")
        if validator.errors:
            print("\nエラー:")
            for error in validator.errors:
                print(f"  {error}")
        if validator.warnings:
            print("\n警告:")
            for warning in validator.warnings:
                print(f"  {warning}")
        sys.exit(1)

if __name__ == "__main__":
    main()

