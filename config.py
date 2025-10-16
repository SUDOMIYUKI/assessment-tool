import os
import sys
from pathlib import Path

# ============================================
# APIキー設定（ここにあなたのAPIキーを貼り付け）
# ============================================
CLAUDE_API_KEY = "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"

# 注意：上記のAPIキーは配布前に必ず設定してください
# 例: CLAUDE_API_KEY = "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ============================================
# パス設定（実行ファイル対応）
# ============================================

if getattr(sys, 'frozen', False):
    # 実行ファイルとして実行されている場合
    BASE_DIR = Path(sys._MEIPASS)
    # ユーザーのドキュメントフォルダに保存
    USER_DIR = Path.home() / 'Documents' / '不登校支援ツール'
else:
    # 開発環境で実行されている場合
    BASE_DIR = Path(__file__).parent
    USER_DIR = BASE_DIR

# ディレクトリ設定
TEMPLATE_DIR = BASE_DIR / 'templates'
OUTPUT_DIR = USER_DIR / 'output'
DATABASE_PATH = USER_DIR / 'data' / 'records.db'

# ディレクトリ作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# API設定
API_MAX_RETRIES = 3
API_RETRY_DELAY = 2
API_TIMEOUT = 60

# ============================================
# APIキーチェック
# ============================================
if not CLAUDE_API_KEY or CLAUDE_API_KEY == "ここにあなたのClaude APIキーを貼り付けてください":
    print("⚠️ 警告: CLAUDE_API_KEYが設定されていません")
    print("config.pyを開いて、APIキーを設定してください")

