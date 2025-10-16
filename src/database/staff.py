import sqlite3
from pathlib import Path
from datetime import datetime

class StaffManager:
    def __init__(self, db_path='data/records.db'):
        self.db_path = Path(db_path)
        self.init_staff_table()
    
    def init_staff_table(self):
        """支援員テーブルを作成"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                region TEXT NOT NULL,
                hobbies_skills TEXT,
                previous_job TEXT,
                dropbox_number TEXT,
                work_days TEXT,
                work_hours TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # サンプルデータを挿入（初回のみ）
        cursor.execute('SELECT COUNT(*) FROM staff')
        if cursor.fetchone()[0] == 0:
            sample_staff = self._get_sample_staff()
            cursor.executemany(
                'INSERT INTO staff (name, age, gender, region, hobbies_skills, previous_job, dropbox_number, work_days, work_hours) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                sample_staff
            )
        
        conn.commit()
        conn.close()
    
    def _get_sample_staff(self):
        """実際の支援員データ（シフト表から詳細抽出）"""
        return [
            # 巽 - 不定期勤務、柔軟対応
            ('巽', 35, '男性', '大阪府大阪市', '柔軟対応、コミュニケーション', '元営業職', 'ST001', '不定期', '14:00-16:00'),
            
            # 岡本 - 火曜日午前、水木金午後
            ('岡本', 28, '女性', '大阪府大阪市', '学校支援、区役所支援', '元教師', 'ST002', '火水木金', '11:00-18:00'),
            
            # 松内 - 全日勤務、サテライト対応
            ('松内', 32, '男性', '大阪府大阪市', 'サテライト支援、自宅支援、区役所支援', '元公務員', 'ST003', '月火水木金', '9:00-17:30'),
            
            # 井上爽 - 木曜日のみ、区役所・自宅支援
            ('井上爽', 29, '女性', '大阪府大阪市', '区役所支援、自宅支援', '元事務職', 'ST004', '木', '10:30-17:30'),
            
            # 山本真美 - 月水、区役所・自宅支援
            ('山本真美', 31, '女性', '大阪府大阪市', '区役所支援、自宅支援', '元看護師', 'ST005', '月水', '11:00-18:00'),
            
            # 末永和久 - 月水、多様な支援形態
            ('末永和久', 38, '男性', '大阪府大阪市', '自宅支援、施設支援、区役所支援', '元社会福祉士', 'ST006', '月水', '10:00-17:30'),
            
            # 藤原佐久夜 - 火木金、登校・区役所・自宅支援
            ('藤原佐久夜', 26, '女性', '大阪府大阪市', '登校支援、区役所支援、自宅支援', '元教育関係', 'ST007', '火木金', '11:00-17:30'),
            
            # 井上智美 - 月火木、隔週・月1回支援
            ('井上智美', 33, '女性', '大阪府大阪市', '隔週支援、月1回支援', '元カウンセラー', 'ST008', '月火木', '10:00-17:30'),
            
            # 田中美由紀 - 全日勤務、自宅・学校支援
            ('田中美由紀', 30, '女性', '大阪府大阪市', '自宅支援、学校支援', '元保育士', 'ST009', '月火水木金', '9:00-16:30'),
            
            # 平岩 - 木金、午後勤務
            ('平岩', 36, '男性', '大阪府大阪市', '自宅支援、区役所支援', '元営業職', 'ST010', '木金', '14:00-17:30'),
            
            # 上田 - 全日勤務、夕方中心
            ('上田', 34, '男性', '大阪府大阪市', '学校支援、区役所支援', '元教員', 'ST011', '月火水木金', '15:30-18:30'),
            
            # 中村 - 水曜日のみ、学校支援
            ('中村', 27, '女性', '大阪府大阪市', '学校支援', '元教育関係', 'ST012', '水', '11:30-18:00'),
            
            # 喜如嘉 - 全日勤務、午後〜夕方
            ('喜如嘉', 40, '女性', '大阪府大阪市', '区役所支援、自宅支援、施設支援', '元社会福祉士', 'ST013', '月火水木金', '13:00-19:00'),
        ]
    
    def add_staff(self, name, age, gender, region, hobbies_skills=None, previous_job=None, dropbox_number=None, work_days=None, work_hours=None):
        """新しい支援員を追加"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO staff (name, age, gender, region, hobbies_skills, previous_job, dropbox_number, work_days, work_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, region, hobbies_skills, previous_job, dropbox_number, work_days, work_hours))
        
        staff_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return staff_id
    
    def get_all_staff(self, active_only=True):
        """全支援員を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('SELECT * FROM staff WHERE is_active = 1 ORDER BY name')
        else:
            cursor.execute('SELECT * FROM staff ORDER BY name')
        
        columns = [description[0] for description in cursor.description]
        staff_list = []
        
        for row in cursor.fetchall():
            staff_dict = dict(zip(columns, row))
            staff_list.append(staff_dict)
        
        conn.close()
        return staff_list
    
    def get_staff_by_id(self, staff_id):
        """IDで支援員を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM staff WHERE id = ?', (staff_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            staff_dict = dict(zip(columns, row))
            conn.close()
            return staff_dict
        
        conn.close()
        return None
    
    def update_staff(self, staff_id, **kwargs):
        """支援員情報を更新"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 更新可能なフィールド
        updatable_fields = ['name', 'age', 'gender', 'region', 'hobbies_skills', 'previous_job', 'dropbox_number', 'work_days', 'work_hours', 'is_active']
        
        update_parts = []
        values = []
        
        for key, value in kwargs.items():
            if key in updatable_fields:
                update_parts.append(f"{key} = ?")
                values.append(value)
        
        if update_parts:
            update_parts.append("updated_at = CURRENT_TIMESTAMP")
            values.append(staff_id)
            
            query = f"UPDATE staff SET {', '.join(update_parts)} WHERE id = ?"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def delete_staff(self, staff_id):
        """支援員を削除（論理削除）"""
        self.update_staff(staff_id, is_active=False)
    
    def search_matching_staff(self, preferred_time=None, preferred_region=None, age_range=None, gender_preference=None, interests=None, preferred_day=None):
        """条件に合う支援員を検索"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 基本クエリ
        query = "SELECT * FROM staff WHERE is_active = 1"
        conditions = []
        params = []
        
        # 地域条件
        if preferred_region:
            # 地域の部分一致で検索（例：東京都 → 東京都の各市区町村）
            conditions.append("region LIKE ?")
            params.append(f"%{preferred_region}%")
        
        # 年齢範囲
        if age_range and len(age_range) == 2:
            min_age, max_age = age_range
            conditions.append("age BETWEEN ? AND ?")
            params.extend([min_age, max_age])
        
        # 性別
        if gender_preference:
            conditions.append("gender = ?")
            params.append(gender_preference)
        
        # 勤務曜日（柔軟な検索）
        if preferred_day:
            # 複数曜日が選択された場合、いずれかがマッチすればOK
            day_conditions = []
            for day in preferred_day:
                day_conditions.append("work_days LIKE ?")
                params.append(f"%{day}%")
            if day_conditions:
                conditions.append(f"({' OR '.join(day_conditions)})")
        
        # 勤務時間（時間帯マッチング）
        if preferred_time and '-' in preferred_time:
            # "開始時間-終了時間"の形式で検索
            time_conditions = []
            time_conditions.append("work_hours LIKE ?")
            params.append(f"%{preferred_time}%")
            
            # さらに柔軟な時間帯マッチング
            try:
                start_str, end_str = preferred_time.split('-')
                start_hour = int(start_str.split(':')[0])
                end_hour = int(end_str.split(':')[0])
                
                # 時間帯が重複する可能性のあるパターンを追加
                for hour in range(start_hour, end_hour + 1):
                    time_conditions.append("work_hours LIKE ?")
                    params.append(f"%{hour:02d}:%")
                
                conditions.append(f"({' OR '.join(time_conditions)})")
            except (ValueError, IndexError):
                # 時間解析に失敗した場合は部分一致のみ
                conditions.append("work_hours LIKE ?")
                params.append(f"%{preferred_time}%")
        
        # 趣味・特技（部分一致）
        if interests:
            interest_conditions = []
            for interest in interests:
                interest_conditions.append("hobbies_skills LIKE ?")
                params.append(f"%{interest}%")
            if interest_conditions:
                conditions.append(f"({' OR '.join(interest_conditions)})")
        
        # クエリを組み立て
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY name"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        staff_list = []
        
        for row in cursor.fetchall():
            staff_dict = dict(zip(columns, row))
            staff_list.append(staff_dict)
        
        conn.close()
        return staff_list
    
    def get_staff_statistics(self):
        """支援員統計情報を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 総数
        cursor.execute('SELECT COUNT(*) FROM staff WHERE is_active = 1')
        total_count = cursor.fetchone()[0]
        
        # 性別別
        cursor.execute('SELECT gender, COUNT(*) FROM staff WHERE is_active = 1 GROUP BY gender')
        gender_stats = dict(cursor.fetchall())
        
        # 年齢別（10歳刻み）
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN age < 30 THEN '20代'
                    WHEN age < 40 THEN '30代'
                    WHEN age < 50 THEN '40代'
                    ELSE '50代以上'
                END as age_group,
                COUNT(*) as count
            FROM staff 
            WHERE is_active = 1 
            GROUP BY age_group
        ''')
        age_stats = dict(cursor.fetchall())
        
        # 地域別
        cursor.execute('SELECT region, COUNT(*) FROM staff WHERE is_active = 1 GROUP BY region ORDER BY count DESC')
        region_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_count': total_count,
            'gender_stats': gender_stats,
            'age_stats': age_stats,
            'region_stats': region_stats
        }
