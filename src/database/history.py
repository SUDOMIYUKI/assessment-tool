import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

# config.pyからDATABASE_PATHを取得
try:
    import config
    DEFAULT_DB_PATH = config.DATABASE_PATH
except (ImportError, AttributeError):
    # config.pyが読み込めない場合はデフォルトパスを使用
    DEFAULT_DB_PATH = Path('data/records.db')

class HistoryManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DEFAULT_DB_PATH
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        self.init_history()
    
    def init_history(self):
        """面談履歴テーブルを作成"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_initials TEXT NOT NULL,
                grade INTEGER,
                gender TEXT,
                school_name TEXT,
                memo TEXT,
                issues_json TEXT,
                short_term_plan_json TEXT,
                long_term_plan_json TEXT,
                future_path_json TEXT,
                medical_info_json TEXT,
                keywords TEXT,
                interview_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 全文検索用インデックス
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON interview_history(keywords)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_grade ON interview_history(grade)')
        
        conn.commit()
        conn.close()
    
    def save_interview(self, interview_data, assessment_data):
        """面談記録を保存"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # キーワード抽出
        keywords = self._extract_keywords(interview_data, assessment_data)
        
        cursor.execute('''
            INSERT INTO interview_history 
            (child_initials, grade, gender, school_name, memo, issues_json, 
             short_term_plan_json, long_term_plan_json, future_path_json, 
             medical_info_json, keywords, interview_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            interview_data.get('児童イニシャル', ''),
            interview_data.get('学年'),
            interview_data.get('性別'),
            interview_data.get('学校名'),
            interview_data.get('メモ'),
            json.dumps(assessment_data.get('issues', {}), ensure_ascii=False),
            json.dumps(assessment_data.get('short_term_plan', {}), ensure_ascii=False),
            json.dumps(assessment_data.get('long_term_plan', {}), ensure_ascii=False),
            json.dumps(assessment_data.get('future_path', {}), ensure_ascii=False),
            json.dumps(interview_data.get('通院状況', {}), ensure_ascii=False),
            keywords,
            interview_data.get('面談実施日').strftime('%Y-%m-%d') if interview_data.get('面談実施日') else None
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ 面談記録を保存しました（ID: {cursor.lastrowid}）")
    
    def _extract_keywords(self, interview_data, assessment_data):
        """検索用キーワードを抽出"""
        keywords = []
        
        # 学年
        grade = interview_data.get('学年')
        if grade:
            if grade <= 6:
                keywords.append('小学生')
            elif grade <= 9:
                keywords.append('中学生')
            else:
                keywords.append('高校生')
        
        # 性別
        if interview_data.get('性別'):
            keywords.append(interview_data.get('性別'))
        
        # 課題
        issues = assessment_data.get('issues', {})
        for issue_name, issue_data in issues.items():
            if issue_data.get('該当'):
                keywords.append(issue_name)
        
        # メモから重要キーワード抽出
        memo = interview_data.get('メモ', '')
        important_words = [
            '不登校', '引きこもり', '昼夜逆転', 'ゲーム', 
            '友達', '対人', '緊張', '不安', 'コミュニケーション',
            '学習', '勉強', '遅れ', '進学', '就職',
            '通院', '診断', '発達', 'ADHD', 'ASD'
        ]
        for word in important_words:
            if word in memo:
                keywords.append(word)
        
        return ' '.join(set(keywords))  # 重複削除
    
    def search_similar_cases(self, current_data, limit=5):
        """類似ケースを検索"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 検索条件を構築
        conditions = []
        params = []
        
        # 学年（±1年）
        grade = current_data.get('学年')
        if grade:
            conditions.append('(grade BETWEEN ? AND ?)')
            params.extend([grade - 1, grade + 1])
        
        # 性別
        gender = current_data.get('性別')
        if gender:
            conditions.append('gender = ?')
            params.append(gender)
        
        # キーワードマッチング
        memo = current_data.get('メモ', '')
        search_keywords = []
        important_words = [
            '不登校', '引きこもり', '昼夜逆転', 'ゲーム', 
            '友達', '対人', '緊張', '不安',
            '学習', '勉強', '進学'
        ]
        for word in important_words:
            if word in memo:
                search_keywords.append(word)
        
        # SQL構築
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        
        # キーワードでスコアリング
        score_conditions = []
        for keyword in search_keywords:
            score_conditions.append(f"CASE WHEN keywords LIKE '%{keyword}%' THEN 1 ELSE 0 END")
        
        score_sql = '+'.join(score_conditions) if score_conditions else '0'
        
        query = f'''
            SELECT id, child_initials, grade, gender, memo, issues_json, 
                   short_term_plan_json, interview_date, keywords,
                   ({score_sql}) as relevance_score
            FROM interview_history
            WHERE {where_clause}
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT ?
        '''
        
        params.append(limit)
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # 整形
        similar_cases = []
        for row in results:
            similar_cases.append({
                'id': row[0],
                'initials': row[1],
                'grade': row[2],
                'gender': row[3],
                'memo': row[4],
                'issues': json.loads(row[5]) if row[5] else {},
                'short_term_plan': json.loads(row[6]) if row[6] else {},
                'interview_date': row[7],
                'keywords': row[8],
                'score': row[9]
            })
        
        conn.close()
        return similar_cases
    
    def get_history_count(self):
        """保存された面談記録数を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM interview_history')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_all_cases(self):
        """すべての面談記録を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, child_initials, grade, gender, school_name, 
                   memo, interview_date, created_at
            FROM interview_history 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results


