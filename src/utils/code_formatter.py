"""
コードフォーマッターとインデント修正機能
"""
import re
from pathlib import Path

class CodeFormatter:
    def __init__(self):
        self.indent_size = 4
        self.indent_char = ' '
    
    def fix_indentation(self, content):
        """インデントを修正"""
        lines = content.split('\n')
        fixed_lines = []
        indent_level = 0
        in_try_block = False
        
        for i, line in enumerate(lines):
            original_line = line
            stripped = line.strip()
            
            # 空行はそのまま
            if not stripped:
                fixed_lines.append(line)
                continue
            
            # コメント行はそのまま
            if stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # tryブロックの開始
            if stripped == 'try:':
                in_try_block = True
                fixed_lines.append(self._indent_line(line, indent_level))
                indent_level += 1
                continue
            
            # except/finallyブロック
            if stripped.startswith('except') or stripped.startswith('finally'):
                in_try_block = False
                indent_level = max(0, indent_level - 1)
                fixed_lines.append(self._indent_line(line, indent_level))
                indent_level += 1
                continue
            
            # 関数定義
            if stripped.startswith('def ') and ':' in stripped:
                indent_level = 0
                fixed_lines.append(line)
                if ':' in stripped:
                    indent_level = 1
                continue
            
            # クラス定義
            if stripped.startswith('class ') and ':' in stripped:
                indent_level = 0
                fixed_lines.append(line)
                if ':' in stripped:
                    indent_level = 1
                continue
            
            # if/for/while文
            if (stripped.startswith(('if ', 'for ', 'while ', 'with ', 'elif ')) or stripped == 'else:') and ':' in stripped:
                # tryブロック内でない場合の特別処理
                if not in_try_block and stripped.startswith(('for ', 'if ')):
                    # 前の行がtry:で終わっている場合
                    if i > 0 and lines[i-1].strip() == 'try:':
                        indent_level = 1
                
                fixed_lines.append(self._indent_line(line, indent_level))
                if ':' in stripped:
                    indent_level += 1
                continue
            
            # 通常の行
            if in_try_block and not line.startswith('    '):
                # tryブロック内の行は必ずインデントが必要
                fixed_lines.append(self._indent_line(line, indent_level))
            else:
                # 既存のインデントを保持
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _indent_line(self, line, level):
        """行にインデントを適用"""
        stripped = line.strip()
        indent = self.indent_char * (level * self.indent_size)
        return indent + stripped
    
    def fix_specific_issues(self, content):
        """特定の問題を修正"""
        # tryブロックの外に出たfor/if文を修正
        lines = content.split('\n')
        fixed_lines = []
        in_try_block = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # tryブロックの開始
            if stripped == 'try:':
                in_try_block = True
                fixed_lines.append(line)
                continue
            
            # except/finallyブロック
            if stripped.startswith('except') or stripped.startswith('finally'):
                in_try_block = False
                fixed_lines.append(line)
                continue
            
            # tryブロック内でfor/if文がインデントされていない場合を修正
            if in_try_block and (stripped.startswith('for ') or stripped.startswith('if ')):
                if not line.startswith('    '):
                    # インデントを追加
                    fixed_lines.append('    ' + stripped)
                    continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def format_file(self, file_path):
        """ファイルをフォーマット"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # バックアップを作成
            backup_path = file_path.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # フォーマット
            fixed_content = self.fix_specific_issues(content)
            fixed_content = self.fix_indentation(fixed_content)
            
            # ファイルに書き戻し
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"✅ {file_path} をフォーマットしました")
            print(f"   バックアップ: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ フォーマットエラー: {file_path}: {e}")
            return False

def main():
    """メイン実行"""
    formatter = CodeFormatter()
    
    # staff_manager.pyをフォーマット
    target_file = Path("src/ui/staff_manager.py")
    
    if target_file.exists():
        print(f"🔧 {target_file} をフォーマット中...")
        if formatter.format_file(target_file):
            print("✅ フォーマット完了")
        else:
            print("❌ フォーマット失敗")
    else:
        print(f"❌ ファイルが見つかりません: {target_file}")

if __name__ == "__main__":
    main()
