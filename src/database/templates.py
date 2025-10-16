import sqlite3
from pathlib import Path

class TemplateManager:
    def __init__(self, db_path='data/records.db'):
        self.db_path = Path(db_path)
        self.init_templates()
    
    def init_templates(self):
        """テンプレートテーブルとデフォルトデータを作成"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # テンプレートテーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phrase_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                phrase TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # デフォルトテンプレートを挿入（初回のみ）
        cursor.execute('SELECT COUNT(*) FROM phrase_templates')
        if cursor.fetchone()[0] == 0:
            default_templates = self._get_default_templates()
            cursor.executemany(
                'INSERT INTO phrase_templates (category, subcategory, phrase) VALUES (?, ?, ?)',
                default_templates
            )
        
        conn.commit()
        conn.close()
    
    def _get_default_templates(self):
        """デフォルトのテンプレートフレーズ"""
        return [
            # 不登校関連
            ('課題', '不登校', '週0回の登校状態が続いている'),
            ('課題', '不登校', '中学1年の秋から不登校が始まった'),
            ('課題', '不登校', '保健室登校は可能だが、教室には入れない'),
            ('課題', '不登校', '登校しようとすると体調不良を訴える'),
            
            # 生活リズム
            ('課題', '生活リズム', '朝起きられず、昼夜逆転している'),
            ('課題', '生活リズム', '夜中までゲームやスマホをしている'),
            ('課題', '生活リズム', '食事が不規則で、朝食を摂らない'),
            ('課題', '生活リズム', '起床時刻が午後になることが多い'),
            
            # 対人関係
            ('課題', '対人関係', '友達との関わりに不安を感じている'),
            ('課題', '対人関係', 'コミュニケーションに苦手意識がある'),
            ('課題', '対人関係', '集団での活動を避けたがる'),
            ('課題', '対人関係', '人と話すときに緊張が強い'),
            
            # 学習
            ('課題', '学習', '学習の遅れが見られる'),
            ('課題', '学習', '学習習慣が定着していない'),
            ('課題', '学習', '勉強への意欲が低下している'),
            ('課題', '学習', '特定の科目に苦手意識が強い'),
            
            # 本人のニーズ
            ('ニーズ', '本人', '友達と話せるようになりたい'),
            ('ニーズ', '本人', 'ゲームを通じて人と交流したい'),
            ('ニーズ', '本人', '自分のペースで過ごしたい'),
            ('ニーズ', '本人', '外に出られるようになりたい'),
            ('ニーズ', '本人', '学校に行けるようになりたい'),
            
            # 保護者のニーズ
            ('ニーズ', '保護者', '学校に戻ってほしい'),
            ('ニーズ', '保護者', '高校進学を実現したい'),
            ('ニーズ', '保護者', '生活リズムを整えてほしい'),
            ('ニーズ', '保護者', '友達と関われるようになってほしい'),
            ('ニーズ', '保護者', '将来に向けて準備してほしい'),
            
            # 短期目標
            ('目標', '短期', '起床時間を9時にする'),
            ('目標', '短期', '週1回は日中に活動する'),
            ('目標', '短期', '週1回の訪問支援を受け入れる'),
            ('目標', '短期', '好きな活動を通じて交流する'),
            ('目標', '短期', '1日1時間、学習時間を確保する'),
            
            # 長期目標
            ('目標', '長期', '段階的な学校復帰を目指す'),
            ('目標', '長期', '高校進学を実現する'),
            ('目標', '長期', '自立した生活習慣を身につける'),
            ('目標', '長期', '対人関係のスキルを向上させる'),
            ('目標', '長期', '社会参加の機会を増やす'),
            
            # 支援方法
            ('方法', '訪問', '週1回の訪問で起床確認と声かけ'),
            ('方法', '訪問', '本人の興味を活かした活動の提供'),
            ('方法', '訪問', '段階的な外出支援（近所の散歩から）'),
            ('方法', '学習', '本人のペースに合わせた学習支援'),
            ('方法', '学習', 'オンライン学習教材の活用'),
            ('方法', '交流', '同じ趣味を持つ仲間との交流機会'),
            ('方法', '交流', 'ゲームを活用した居場所づくり'),
            ('方法', '家族', '保護者との定期的な情報共有'),
            ('方法', '家族', '家族の負担軽減のための相談支援'),
            
            # 進路
            ('進路', '進学', '高校進学を希望（具体的な学校は未定）'),
            ('進路', '進学', '通信制高校を検討中'),
            ('進路', '進学', '定時制高校に興味がある'),
            ('進路', '就職', '将来は働きたいと考えている'),
            ('進路', '就職', '職業体験に興味がある'),
        ]
    
    def get_templates(self, category=None, subcategory=None):
        """テンプレートを取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if category and subcategory:
            cursor.execute(
                'SELECT id, phrase FROM phrase_templates WHERE category=? AND subcategory=? ORDER BY usage_count DESC',
                (category, subcategory)
            )
        elif category:
            cursor.execute(
                'SELECT id, phrase FROM phrase_templates WHERE category=? ORDER BY usage_count DESC',
                (category,)
            )
        else:
            cursor.execute(
                'SELECT id, category, subcategory, phrase FROM phrase_templates ORDER BY category, subcategory, usage_count DESC'
            )
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_categories(self):
        """カテゴリ一覧を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM phrase_templates ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_subcategories(self, category):
        """サブカテゴリ一覧を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            'SELECT DISTINCT subcategory FROM phrase_templates WHERE category=? ORDER BY subcategory',
            (category,)
        )
        subcategories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return subcategories
    
    def increment_usage(self, phrase_id):
        """使用回数をカウント"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE phrase_templates SET usage_count = usage_count + 1 WHERE id = ?',
            (phrase_id,)
        )
        conn.commit()
        conn.close()
    
    def add_custom_phrase(self, category, subcategory, phrase):
        """カスタムフレーズを追加"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO phrase_templates (category, subcategory, phrase) VALUES (?, ?, ?)',
            (category, subcategory, phrase)
        )
        conn.commit()
        conn.close()
    
    def import_from_history(self):
        """過去のケースからテンプレートを自動生成"""
        from src.database.history import HistoryManager
        
        history_manager = HistoryManager()
        all_cases = history_manager.get_all_cases()
        
        new_templates = []
        
        for case_tuple in all_cases:
            # タプルを辞書に変換 (id, child_initials, grade, gender, school_name, memo, interview_date, created_at)
            if len(case_tuple) >= 8:
                case = {
                    'id': case_tuple[0],
                    'child_initials': case_tuple[1],
                    'grade': case_tuple[2],
                    'gender': case_tuple[3],
                    'school_name': case_tuple[4],
                    'memo': case_tuple[5],
                    'interview_date': case_tuple[6],
                    'created_at': case_tuple[7]
                }
                
                # メモからテンプレートを抽出
                memo = case.get('memo', '')
                if memo:
                    # メモの内容から課題関連のフレーズを抽出
                    lines = memo.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 10:  # 短すぎる行は除外
                            # 課題関連のキーワードでフィルタリング
                            if any(keyword in line for keyword in ['不登校', '登校', '学校', '学習', '生活', '人間関係', '家族', '進路']):
                                new_templates.append(('課題', 'メモから抽出', line))
            
            # 支援計画からテンプレートを抽出（過去のケースがある場合）
            # 現在はメモからの抽出のみ実装
            pass
        
        # 重複を除去してテンプレートを追加
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for category, subcategory, phrase in new_templates:
            # 既存チェック
            cursor.execute(
                'SELECT COUNT(*) FROM phrase_templates WHERE category=? AND subcategory=? AND phrase=?',
                (category, subcategory, phrase)
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    'INSERT INTO phrase_templates (category, subcategory, phrase) VALUES (?, ?, ?)',
                    (category, subcategory, phrase)
                )
        
        conn.commit()
        conn.close()
        
        return len(new_templates)
    
    def get_popular_templates(self, category=None, subcategory=None, limit=20):
        """人気のテンプレートを取得（使用回数順）"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if category and subcategory:
            cursor.execute(
                'SELECT id, phrase FROM phrase_templates WHERE category=? AND subcategory=? ORDER BY usage_count DESC, id DESC LIMIT ?',
                (category, subcategory, limit)
            )
        elif category:
            cursor.execute(
                'SELECT id, phrase FROM phrase_templates WHERE category=? ORDER BY usage_count DESC, id DESC LIMIT ?',
                (category, limit)
            )
        else:
            cursor.execute(
                'SELECT id, category, subcategory, phrase FROM phrase_templates ORDER BY usage_count DESC, id DESC LIMIT ?',
                (limit,)
            )
        
        results = cursor.fetchall()
        conn.close()
        return results


