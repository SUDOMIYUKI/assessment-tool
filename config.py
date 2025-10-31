#!/usr/bin/env python3
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
# Dropbox設定
# ============================================

# Dropbox連携を有効化するか
USE_DROPBOX = True  # Trueで自動的にDropboxに保存、Falseで通常のoutputフォルダに保存

# Dropboxフォルダのパスを自動検出
DROPBOX_PATH = Path.home() / 'Dropbox'

# Dropboxが存在しない場合の代替パスリスト
DROPBOX_ALTERNATIVES = [
    Path.home() / 'Dropbox',
    Path.home() / 'Dropbox (Personal)',
    Path.home() / 'Dropbox (Business)',
    Path('C:/Dropbox') if os.name == 'nt' else None,
]

def get_dropbox_path():
    """Dropboxフォルダのパスを取得"""
    for path in DROPBOX_ALTERNATIVES:
        if path and path.exists():
            return path
    return None

# Dropboxが利用可能かチェック
def check_dropbox_available():
    """Dropboxが利用可能か確認"""
    if not USE_DROPBOX:
        return False
    return get_dropbox_path() is not None

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

# 出力ディレクトリの設定（Dropbox優先）
if USE_DROPBOX and check_dropbox_available():
    dropbox_path = get_dropbox_path()
    OUTPUT_DIR = dropbox_path / '不登校支援ツール' / 'output'
    print(f"✅ Dropbox連携が有効です: {OUTPUT_DIR}")
else:
    OUTPUT_DIR = USER_DIR / 'output'
    if USE_DROPBOX:
        print("⚠️ Dropboxフォルダが見つかりません。ローカルに保存します。")

DATABASE_PATH = USER_DIR / 'data' / 'records.db'

# ディレクトリ作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# API設定
API_MAX_RETRIES = 3
API_RETRY_DELAY = 2
API_TIMEOUT = 60

# Excel設定
EXCEL_PASSWORD = None  # パスワード保護する場合は文字列を設定（例: "password123"）

# ============================================
# APIキーチェック
# ============================================
if not CLAUDE_API_KEY or CLAUDE_API_KEY == "ここにあなたのClaude APIキーを貼り付けてください":
    print("⚠️ 警告: CLAUDE_API_KEYが設定されていません")
    print("config.pyを開いて、APIキーを設定してください")

# ============================================
# アプリケーション設定
# ============================================

APP_VERSION = "1.0.0"
APP_NAME = "不登校支援 - 初回アセスメント支援ツール"

# デバッグモード
DEBUG = False

if DEBUG:
    print("=" * 60)
    print("🔧 設定情報")
    print("=" * 60)
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"USER_DIR: {USER_DIR}")
    print(f"OUTPUT_DIR: {OUTPUT_DIR}")
    print(f"DATABASE_PATH: {DATABASE_PATH}")
    print(f"TEMPLATE_DIR: {TEMPLATE_DIR}")
    print(f"Dropbox連携: {'有効' if USE_DROPBOX else '無効'}")
    print(f"Dropboxパス: {get_dropbox_path() if check_dropbox_available() else 'なし'}")
    print("=" * 60)
