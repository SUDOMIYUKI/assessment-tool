import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path='data/records.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_name_encrypted TEXT NOT NULL,
                initials TEXT NOT NULL,
                gender TEXT,
                school_name TEXT,
                grade INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                interview_date DATE NOT NULL,
                interviewer TEXT,
                guardian_name TEXT,
                memo_encrypted TEXT,
                medical_info TEXT,
                ai_analysis_result TEXT,
                assessment_file_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quick_phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase TEXT NOT NULL,
                category TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_child_name ON children(child_name_encrypted)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interview_date ON interviews(interview_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_child_initials ON children(initials)')
        
        conn.commit()
        conn.close()
        print("データベースを初期化しました")

