import sqlite3
from pathlib import Path
from datetime import datetime

class StaffManager:
    def __init__(self, db_path='data/records.db'):
        self.db_path = Path(db_path)
        self.init_staff_table()
        self.init_enhanced_tables()
    
    def init_staff_table(self):
        """支援員テーブルを作成"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
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
                case_district TEXT,
                case_number TEXT,
                case_day TEXT,
                case_time TEXT,
                case_frequency TEXT,
                case_location TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 既存のテーブルに新しいカラムを追加（マイグレーション）
        try:
            cursor.execute('ALTER TABLE staff ADD COLUMN case_district TEXT')
            cursor.execute('ALTER TABLE staff ADD COLUMN case_number TEXT')
            cursor.execute('ALTER TABLE staff ADD COLUMN case_day TEXT')
            cursor.execute('ALTER TABLE staff ADD COLUMN case_time TEXT')
            cursor.execute('ALTER TABLE staff ADD COLUMN case_frequency TEXT')
            cursor.execute('ALTER TABLE staff ADD COLUMN case_location TEXT')
            cursor.execute('ALTER TABLE staff ADD COLUMN notes TEXT')
        except sqlite3.OperationalError:
            # カラムが既に存在する場合は無視
            pass
        
        # サンプルデータを挿入（初回のみ）
        cursor.execute('SELECT COUNT(*) FROM staff')
        if cursor.fetchone()[0] == 0:
            sample_staff = self._get_sample_staff()
            cursor.executemany(
                'INSERT INTO staff (name, age, gender, region, hobbies_skills, previous_job, dropbox_number, work_days, work_hours, case_district, case_number, case_day, case_time, case_frequency, case_location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                sample_staff
            )
        
        conn.commit()
        conn.close()
    
    def _get_sample_staff(self):
        """実際の支援員データ（シフト表から詳細抽出）"""
        return [
            # 巽 - 不定期勤務、柔軟対応
            ('巽', 35, '男性', '大阪府大阪市', '柔軟対応、コミュニケーション', '元営業職', 'ST001', '不定期', '14:00-16:00', '大阪市住之江区', 'C001', '火', '14:00-16:00', '週1回', '自宅'),
            
            # 岡本 - 火曜日午前、水木金午後
            ('岡本', 28, '女性', '大阪府大阪市', '学校支援、区役所支援', '元教師', 'ST002', '火水木金', '11:00-18:00', '大阪市西区', 'C002', '水', '11:00-18:00', '週1回', '区役所'),
            
            # 松内 - 全日勤務、サテライト対応
            ('松内', 32, '男性', '大阪府大阪市', 'サテライト支援、自宅支援、区役所支援', '元公務員', 'ST003', '月火水木金', '9:00-17:30', '大阪市中央区', 'C003', '木', '9:00-17:30', '週1回', 'サテライト'),
            
            # 井上爽 - 木曜日のみ、区役所・自宅支援
            ('井上爽', 29, '女性', '大阪府大阪市', '区役所支援、自宅支援', '元事務職', 'ST004', '木', '10:30-17:30', '大阪市東区', 'C004', '木', '10:30-17:30', '週1回', '自宅'),
            
            # 山本真美 - 月水、区役所・自宅支援
            ('山本真美', 31, '女性', '大阪府大阪市', '区役所支援、自宅支援', '元看護師', 'ST005', '月水', '11:00-18:00', '大阪市北区', 'C005', '月', '11:00-18:00', '週1回', '区役所'),
            
            # 末永和久 - 月水、多様な支援形態
            ('末永和久', 38, '男性', '大阪府大阪市', '自宅支援、施設支援、区役所支援', '元社会福祉士', 'ST006', '月水', '10:00-17:30', '大阪市南区', 'C006', '水', '10:00-17:30', '週1回', '施設'),
            
            # 藤原佐久夜 - 火木金、登校・区役所・自宅支援
            ('藤原佐久夜', 26, '女性', '大阪府大阪市', '登校支援、区役所支援、自宅支援', '元教育関係', 'ST007', '火木金', '11:00-17:30', '大阪市西成区', 'C007', '金', '11:00-17:30', '週1回', '学校'),
            
            # 井上智美 - 月火木、隔週・月1回支援
            ('井上智美', 33, '女性', '大阪府大阪市', '隔週支援、月1回支援', '元カウンセラー', 'ST008', '月火木', '10:00-17:30', '大阪市阿倍野区', 'C008', '火', '10:00-17:30', '隔週', '自宅'),
            
            # 田中美由紀 - 全日勤務、自宅・学校支援
            ('田中美由紀', 30, '女性', '大阪府大阪市', '自宅支援、学校支援', '元保育士', 'ST009', '月火水木金', '9:00-16:30', '大阪市天王寺区', 'C009', '月', '9:00-16:30', '週1回', '自宅'),
            
            # 平岩 - 木金、午後勤務
            ('平岩', 36, '男性', '大阪府大阪市', '自宅支援、区役所支援', '元営業職', 'ST010', '木金', '14:00-17:30', '大阪市福島区', 'C010', '金', '14:00-17:30', '週1回', '自宅'),
            
            # 上田 - 全日勤務、夕方中心
            ('上田', 34, '男性', '大阪府大阪市', '学校支援、区役所支援', '元教員', 'ST011', '月火水木金', '15:30-18:30', '大阪市此花区', 'C011', '水', '15:30-18:30', '週1回', '学校'),
            
            # 中村 - 水曜日のみ、学校支援
            ('中村', 27, '女性', '大阪府大阪市', '学校支援', '元教育関係', 'ST012', '水', '11:30-18:00', '大阪市港区', 'C012', '水', '11:30-18:00', '週1回', '学校'),
            
            # 喜如嘉 - 全日勤務、午後〜夕方
            ('喜如嘉', 40, '女性', '大阪府大阪市', '区役所支援、自宅支援、施設支援', '元社会福祉士', 'ST013', '月火水木金', '13:00-19:00', '大阪市大正区', 'C013', '木', '13:00-19:00', '週1回', '施設'),
        ]
    
    def add_staff(self, staff_data=None, **kwargs):
        """新しい支援員を追加"""
        # 辞書形式のデータまたは個別引数に対応
        if staff_data and isinstance(staff_data, dict):
            # 辞書形式の場合
            name = staff_data.get('name')
            age = staff_data.get('age')
            gender = staff_data.get('gender')
            region = staff_data.get('region')
            hobbies_skills = staff_data.get('hobbies_skills')
            previous_job = staff_data.get('previous_job')
            dropbox_number = staff_data.get('dropbox_number')
            work_days = staff_data.get('work_days')
            work_hours = staff_data.get('work_hours')
            case_district = staff_data.get('case_district')
            case_number = staff_data.get('case_number')
            case_day = staff_data.get('case_day')
            case_time = staff_data.get('case_time')
            case_frequency = staff_data.get('case_frequency')
            case_location = staff_data.get('case_location')
            notes = staff_data.get('notes')
        else:
            # 個別引数の場合（後方互換性のため）
            name = kwargs.get('name')
            age = kwargs.get('age')
            gender = kwargs.get('gender')
            region = kwargs.get('region')
            hobbies_skills = kwargs.get('hobbies_skills')
            previous_job = kwargs.get('previous_job')
            dropbox_number = kwargs.get('dropbox_number')
            work_days = kwargs.get('work_days')
            work_hours = kwargs.get('work_hours')
            case_district = kwargs.get('case_district')
            case_number = kwargs.get('case_number')
            case_day = kwargs.get('case_day')
            case_time = kwargs.get('case_time')
            case_frequency = kwargs.get('case_frequency')
            case_location = kwargs.get('case_location')
            notes = kwargs.get('notes')
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO staff (name, age, gender, region, hobbies_skills, previous_job, dropbox_number, work_days, work_hours, case_district, case_number, case_day, case_time, case_frequency, case_location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, region, hobbies_skills, previous_job, dropbox_number, work_days, work_hours, case_district, case_number, case_day, case_time, case_frequency, case_location, notes))
        
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
    
    def update_staff(self, staff_id, staff_data=None, **kwargs):
        """支援員情報を更新"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 更新可能なフィールド
        updatable_fields = ['name', 'age', 'gender', 'region', 'hobbies_skills', 'previous_job', 'dropbox_number', 'work_days', 'work_hours', 'case_district', 'case_number', 'case_day', 'case_time', 'case_frequency', 'case_location', 'notes', 'is_active']
        
        update_parts = []
        values = []
        
        # 辞書形式のデータまたは個別引数に対応
        if staff_data and isinstance(staff_data, dict):
            update_data = staff_data
        else:
            update_data = kwargs
        
        for key, value in update_data.items():
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
    
    def search_matching_staff(self, preferred_time=None, preferred_region=None, age_range=None, gender_preference=None, interests=None, preferred_day=None, exclude_occupied_times=True):
        """条件に合う支援員を検索（重複チェック機能付き）"""
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
        
        # 重複チェック：既にケースを持っている支援員を除外
        if exclude_occupied_times and preferred_day and preferred_time:
            # 指定された曜日・時間帯に既にケースを持っている支援員を除外
            occupied_conditions = []
            for day in preferred_day:
                occupied_conditions.append("(case_day = ? AND case_time LIKE ?)")
                params.extend([day, f"%{preferred_time}%"])
            
            if occupied_conditions:
                conditions.append(f"NOT ({' OR '.join(occupied_conditions)})")
        
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

    def init_enhanced_tables(self):
        """拡張テーブルを作成"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        cursor = conn.cursor()
        
        # 未割り当てケース管理テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unassigned_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT NOT NULL UNIQUE,
                district TEXT,
                child_name TEXT,
                child_age INTEGER,
                child_gender TEXT,
                preferred_day TEXT,
                preferred_time TEXT,
                frequency TEXT,
                location TEXT,
                notes TEXT,
                status TEXT DEFAULT '未割り当て',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # エリアマスタテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_order INTEGER
            )
        ''')
        
        # 区マスタテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                area_id INTEGER NOT NULL,
                display_order INTEGER,
                FOREIGN KEY (area_id) REFERENCES areas(id)
            )
        ''')
        
        # ケーステーブル（多対多対応）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT NOT NULL,
                district_id INTEGER NOT NULL,
                phone_number TEXT,
                child_name TEXT,
                child_last_name TEXT,
                child_first_name TEXT,
                schedule_day TEXT,
                schedule_time TEXT,
                location TEXT,
                first_meeting_date DATE,
                frequency TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (district_id) REFERENCES districts(id)
            )
        ''')
        
        # 既存のテーブルに新しいカラムを追加（マイグレーション）
        try:
            cursor.execute('ALTER TABLE cases ADD COLUMN child_last_name TEXT')
            cursor.execute('ALTER TABLE cases ADD COLUMN child_first_name TEXT')
        except sqlite3.OperationalError:
            # カラムが既に存在する場合は無視
            pass
        
        # 支援員とケースの関連テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                case_id INTEGER NOT NULL,
                assigned_date DATE DEFAULT CURRENT_DATE,
                is_primary BOOLEAN DEFAULT 1,
                FOREIGN KEY (staff_id) REFERENCES staff(id),
                FOREIGN KEY (case_id) REFERENCES cases(id),
                UNIQUE(staff_id, case_id)
            )
        ''')
        
        # 週間スケジュールテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                case_id INTEGER,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                schedule_type TEXT,
                color_code TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (staff_id) REFERENCES staff(id),
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        ''')
        
        # 初期データ投入
        cursor.execute('SELECT COUNT(*) FROM areas')
        if cursor.fetchone()[0] == 0:
            # エリアデータ
            cursor.executemany(
                'INSERT INTO areas (name, display_order) VALUES (?, ?)',
                [('東エリア', 1), ('南エリア', 2)]
            )
            
            # 区データ
            districts_data = [
                # 東エリア (id=1)
                ('城東区', 1, 1),
                ('鶴見区', 1, 2),
                ('天王寺区', 1, 3),
                ('中央区', 1, 4),
                ('浪速区', 1, 5),
                ('生野区', 1, 6),
                ('東成区', 1, 7),
                # 南エリア (id=2)
                ('阿倍野区', 2, 8),
                ('平野区', 2, 9),
                ('住吉区', 2, 10),
                ('東住吉区', 2, 11),
                ('西成区', 2, 12),
            ]
            cursor.executemany(
                'INSERT INTO districts (name, area_id, display_order) VALUES (?, ?, ?)',
                districts_data
            )
        
        conn.commit()
        conn.close()

    def get_all_districts(self):
        """全区を取得（エリア別）"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.id, d.name, a.name as area_name, d.display_order
            FROM districts d
            JOIN areas a ON d.area_id = a.id
            ORDER BY d.display_order
        ''')
        
        columns = ['id', 'name', 'area_name', 'display_order']
        districts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return districts

    def get_staff_with_cases(self, staff_id):
        """支援員のケース情報を含めて取得"""
        if not staff_id:
            return []
            
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            staff_id_int = int(staff_id)
            cursor.execute('''
                SELECT 
                    c.id, c.case_number, c.district_id, d.name as district_name,
                    c.phone_number, c.child_name, c.child_last_name, c.child_first_name,
                    c.schedule_day, c.schedule_time, c.location, c.first_meeting_date,
                    c.frequency, c.notes
                FROM cases c
                JOIN staff_cases sc ON c.id = sc.case_id
                JOIN districts d ON c.district_id = d.id
                WHERE sc.staff_id = ? AND c.is_active = 1
                ORDER BY c.schedule_day, c.schedule_time
            ''', (staff_id_int,))
            
            columns = [desc[0] for desc in cursor.description]
            cases = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except (ValueError, TypeError) as e:
            print(f"get_staff_with_cases エラー: staff_idが無効です - {staff_id}: {e}")
            cases = []
        except Exception as e:
            print(f"get_staff_with_cases エラー: {e}")
            cases = []
        finally:
            conn.close()
        
        return cases

    def add_case_to_staff(self, staff_id, case_data):
        """支援員にケースを追加"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # ケースを作成（苗字と下の名前を結合してchild_nameにも保存）
        child_last_name = case_data.get('child_last_name', '').strip()
        child_first_name = case_data.get('child_first_name', '').strip()
        child_name = f"{child_last_name} {child_first_name}".strip() if (child_last_name or child_first_name) else ''
        
        cursor.execute('''
            INSERT INTO cases 
            (case_number, district_id, phone_number, child_name, child_last_name, child_first_name,
             schedule_day, schedule_time, location, first_meeting_date, 
             frequency, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case_data.get('case_number'),
            case_data.get('district_id'),
            case_data.get('phone_number'),
            child_name,
            child_last_name,
            child_first_name,
            case_data.get('schedule_day'),
            case_data.get('schedule_time'),
            case_data.get('location'),
            case_data.get('first_meeting_date'),
            case_data.get('frequency'),
            case_data.get('notes')
        ))
        
        case_id = cursor.lastrowid
        
        # 支援員とケースを関連付け
        cursor.execute('''
            INSERT INTO staff_cases (staff_id, case_id)
            VALUES (?, ?)
        ''', (staff_id, case_id))
        
        # スケジュールエントリを作成（ケースの曜日・時間情報から）
        schedule_day = case_data.get('schedule_day', '')
        schedule_time = case_data.get('schedule_time', '')
        location = case_data.get('location', '')
        
        if schedule_day and schedule_time:
            # 曜日のマッピング
            day_mapping = {
                '月': '月',
                '火': '火',
                '水': '水',
                '木': '木',
                '金': '金'
            }
            
            # 時間の解析（「14:00」または「14:00-16:00」形式）
            # 全角コロン（：）や波線（～）を半角に変換
            schedule_time = schedule_time.replace('：', ':').replace('～', '-').replace('~', '-').strip()
            
            if '-' in schedule_time:
                # 範囲形式（例: 「14:00-16:00」）
                time_parts = schedule_time.split('-')
                start_time = time_parts[0].strip()
                end_time = time_parts[1].strip()
            else:
                # 単一時間形式（例: 「14:00」）- 1時間のセッションとして扱う
                start_time = schedule_time.strip()
                # 終了時間を計算（1時間後）
                try:
                    # コロンで分割して時間と分を取得
                    if ':' in start_time:
                        hour, minute = start_time.split(':')
                        hour_int = int(hour)
                        minute_int = int(minute) if minute else 0
                    else:
                        # コロンがない場合は時間のみ
                        hour_int = int(start_time)
                        minute_int = 0
                        start_time = f"{hour_int:02d}:{minute_int:02d}"
                    
                    end_hour = hour_int + 1
                    end_time = f"{end_hour:02d}:{minute_int:02d}"
                except Exception as e:
                    print(f"⚠️ 時間解析エラー: {e}, 時間: {start_time}, デフォルトで1時間後に設定")
                    # エラー時は開始時間から1時間後を設定
                    try:
                        hour_int = int(start_time.split(':')[0]) if ':' in start_time else int(start_time)
                        end_hour = hour_int + 1
                        end_time = f"{end_hour:02d}:00"
                    except:
                        # 最後のフォールバック：デフォルトで1時間後
                        end_time = f"{(int(start_time.replace(':', '')) // 100 + 1):02d}:00" if start_time else "15:00"
            
            # 各曜日ごとにスケジュールエントリを作成
            for day_char in schedule_day:
                if day_char in day_mapping:
                    day_of_week = day_mapping[day_char]
                    try:
                        # schedulesテーブルの存在を確認
                        cursor.execute('''
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name='schedules'
                        ''')
                        if not cursor.fetchone():
                            print("⚠️ schedulesテーブルが存在しません。init_enhanced_tablesを呼び出してください。")
                            # テーブルが存在しない場合は作成を試みる
                            self.init_enhanced_tables()
                        
                        cursor.execute('''
                            INSERT INTO schedules 
                            (staff_id, case_id, day_of_week, start_time, end_time, location, schedule_type, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            staff_id,
                            case_id,
                            day_of_week,
                            start_time,
                            end_time,
                            location,
                            'ケース',
                            1
                        ))
                        print(f"✅ スケジュールエントリ作成: {day_of_week} {start_time}-{end_time}")
                    except Exception as e:
                        print(f"❌ スケジュールエントリ作成エラー: {e}")
                        import traceback
                        traceback.print_exc()
        
        conn.commit()
        conn.close()
        
        return case_id
    
    def get_case_by_id(self, case_id):
        """ケースIDからケース情報を取得"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    c.id, c.case_number, c.district_id, d.name as district_name, a.name as area_name,
                    c.phone_number, c.child_name, c.child_last_name, c.child_first_name,
                    c.schedule_day, c.schedule_time, c.location, c.first_meeting_date,
                    c.frequency, c.notes
                FROM cases c
                LEFT JOIN districts d ON c.district_id = d.id
                LEFT JOIN areas a ON d.area_id = a.id
                WHERE c.id = ? AND c.is_active = 1
            ''', (case_id,))
            
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            if row:
                case = dict(zip(columns, row))
            else:
                case = None
        except Exception as e:
            print(f"get_case_by_id エラー: {e}")
            case = None
        finally:
            conn.close()
        
        return case
    
    def update_case_to_staff(self, case_id, case_data):
        """ケース情報を更新"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # ケース情報を更新（苗字と下の名前を結合してchild_nameにも保存）
            child_last_name = case_data.get('child_last_name', '').strip()
            child_first_name = case_data.get('child_first_name', '').strip()
            child_name = f"{child_last_name} {child_first_name}".strip() if (child_last_name or child_first_name) else ''
            
            cursor.execute('''
                UPDATE cases 
                SET case_number = ?,
                    district_id = ?,
                    phone_number = ?,
                    child_name = ?,
                    child_last_name = ?,
                    child_first_name = ?,
                    schedule_day = ?,
                    schedule_time = ?,
                    location = ?,
                    first_meeting_date = ?,
                    frequency = ?,
                    notes = ?
                WHERE id = ?
            ''', (
                case_data.get('case_number'),
                case_data.get('district_id'),
                case_data.get('phone_number'),
                child_name,
                child_last_name,
                child_first_name,
                case_data.get('schedule_day'),
                case_data.get('schedule_time'),
                case_data.get('location'),
                case_data.get('first_meeting_date'),
                case_data.get('frequency'),
                case_data.get('notes'),
                case_id
            ))
            
            # 既存のスケジュールエントリを削除
            cursor.execute('''
                DELETE FROM schedules 
                WHERE case_id = ?
            ''', (case_id,))
            
            # 新しいスケジュールエントリを作成
            schedule_day = case_data.get('schedule_day', '')
            schedule_time = case_data.get('schedule_time', '')
            location = case_data.get('location', '')
            
            # ケースに紐づく支援員IDを取得
            cursor.execute('''
                SELECT staff_id FROM staff_cases 
                WHERE case_id = ?
                LIMIT 1
            ''', (case_id,))
            staff_result = cursor.fetchone()
            staff_id = staff_result[0] if staff_result else None
            
            if schedule_day and schedule_time and staff_id:
                # 曜日のマッピング
                day_mapping = {
                    '月': '月',
                    '火': '火',
                    '水': '水',
                    '木': '木',
                    '金': '金'
                }
                
                # 時間の解析（全角コロンや波線を半角に変換）
                schedule_time_normalized = schedule_time.replace('：', ':').replace('～', '-').replace('~', '-').strip()
                
                if '-' in schedule_time_normalized:
                    time_parts = schedule_time_normalized.split('-')
                    start_time = time_parts[0].strip()
                    end_time = time_parts[1].strip()
                else:
                    start_time = schedule_time_normalized.strip()
                    # 終了時間を計算（1時間後）
                    try:
                        # コロンで分割して時間と分を取得
                        if ':' in start_time:
                            hour, minute = start_time.split(':')
                            hour_int = int(hour)
                            minute_int = int(minute) if minute else 0
                        else:
                            # コロンがない場合は時間のみ
                            hour_int = int(start_time)
                            minute_int = 0
                            start_time = f"{hour_int:02d}:{minute_int:02d}"
                        
                        end_hour = hour_int + 1
                        end_time = f"{end_hour:02d}:{minute_int:02d}"
                    except Exception as e:
                        print(f"⚠️ 時間解析エラー（update）: {e}, 時間: {start_time}, デフォルトで1時間後に設定")
                        # エラー時は開始時間から1時間後を設定
                        try:
                            hour_int = int(start_time.split(':')[0]) if ':' in start_time else int(start_time)
                            end_hour = hour_int + 1
                            end_time = f"{end_hour:02d}:00"
                        except:
                            end_time = f"15:00"  # 最後のフォールバック
                
                # 各曜日ごとにスケジュールエントリを作成
                for day_char in schedule_day:
                    if day_char in day_mapping:
                        day_of_week = day_mapping[day_char]
                        try:
                            cursor.execute('''
                                INSERT INTO schedules 
                                (staff_id, case_id, day_of_week, start_time, end_time, location, schedule_type, is_active)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                staff_id,
                                case_id,
                                day_of_week,
                                start_time,
                                end_time,
                                location,
                                'ケース',
                                1
                            ))
                            print(f"✅ スケジュールエントリ更新: {day_of_week} {start_time}-{end_time}")
                        except Exception as e:
                            print(f"❌ スケジュールエントリ更新エラー: {e}")
            
            conn.commit()
            print(f"✅ ケース情報を更新しました（ID: {case_id}）")
        except Exception as e:
            print(f"update_case_to_staff エラー: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            conn.close()
        
        return case_id

    def sync_all_cases_to_schedule(self):
        """既存のケースからスケジュールエントリを生成（スケジュールエントリがない場合）"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # 全てのケースとその支援員を取得
            cursor.execute('''
                SELECT 
                    c.id as case_id,
                    c.schedule_day,
                    c.schedule_time,
                    c.location,
                    sc.staff_id
                FROM cases c
                JOIN staff_cases sc ON c.id = sc.case_id
                WHERE c.is_active = 1
                  AND c.schedule_day IS NOT NULL 
                  AND c.schedule_day != ''
                  AND c.schedule_time IS NOT NULL 
                  AND c.schedule_time != ''
            ''')
            
            cases = cursor.fetchall()
            created_count = 0
            
            # 曜日のマッピング
            day_mapping = {
                '月': '月',
                '火': '火',
                '水': '水',
                '木': '木',
                '金': '金'
            }
            
            for case_id, schedule_day, schedule_time, location, staff_id in cases:
                # 既にスケジュールエントリが存在するかチェック
                cursor.execute('''
                    SELECT COUNT(*) FROM schedules 
                    WHERE case_id = ? AND is_active = 1
                ''', (case_id,))
                
                if cursor.fetchone()[0] > 0:
                    # 既にスケジュールエントリが存在する場合はスキップ
                    continue
                
                # 時間の解析（全角コロンや波線を半角に変換）
                schedule_time_normalized = schedule_time.replace('：', ':').replace('～', '-').replace('~', '-').strip()
                
                if '-' in schedule_time_normalized:
                    time_parts = schedule_time_normalized.split('-')
                    start_time = time_parts[0].strip()
                    end_time = time_parts[1].strip()
                else:
                    start_time = schedule_time_normalized.strip()
                    # 終了時間を計算（1時間後）
                    try:
                        # コロンで分割して時間と分を取得
                        if ':' in start_time:
                            hour, minute = start_time.split(':')
                            hour_int = int(hour)
                            minute_int = int(minute) if minute else 0
                        else:
                            # コロンがない場合は時間のみ
                            hour_int = int(start_time)
                            minute_int = 0
                            start_time = f"{hour_int:02d}:{minute_int:02d}"
                        
                        end_hour = hour_int + 1
                        end_time = f"{end_hour:02d}:{minute_int:02d}"
                    except Exception as e:
                        print(f"⚠️ 時間解析エラー（update）: {e}, 時間: {start_time}, デフォルトで1時間後に設定")
                        # エラー時は開始時間から1時間後を設定
                        try:
                            hour_int = int(start_time.split(':')[0]) if ':' in start_time else int(start_time)
                            end_hour = hour_int + 1
                            end_time = f"{end_hour:02d}:00"
                        except:
                            end_time = f"15:00"  # 最後のフォールバック
                
                # 各曜日ごとにスケジュールエントリを作成
                for day_char in schedule_day:
                    if day_char in day_mapping:
                        day_of_week = day_mapping[day_char]
                        try:
                            cursor.execute('''
                                INSERT INTO schedules 
                                (staff_id, case_id, day_of_week, start_time, end_time, location, schedule_type, is_active)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                staff_id,
                                case_id,
                                day_of_week,
                                start_time,
                                end_time,
                                location,
                                'ケース',
                                1
                            ))
                            created_count += 1
                        except Exception as e:
                            print(f"❌ スケジュールエントリ作成エラー（ケースID: {case_id}）: {e}")
            
            conn.commit()
            if created_count > 0:
                print(f"✅ 既存ケースから{created_count}個のスケジュールエントリを作成しました")
        except Exception as e:
            print(f"sync_all_cases_to_schedule エラー: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()
    
    def get_weekly_schedule(self):
        """週間スケジュールを取得（既存ケースからスケジュールエントリを自動生成）"""
        # 既存ケースからスケジュールエントリを生成（初回のみ）
        self.sync_all_cases_to_schedule()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    s.id, s.day_of_week, s.start_time, s.end_time,
                    s.location, s.schedule_type, s.color_code,
                    staff.name as staff_name, c.case_number,
                    d.name as district_name, c.child_name, c.child_first_name,
                    c.frequency
                FROM schedules s
                JOIN staff ON s.staff_id = staff.id
                LEFT JOIN cases c ON s.case_id = c.id
                LEFT JOIN districts d ON c.district_id = d.id
                WHERE s.is_active = 1
                ORDER BY s.day_of_week, s.start_time
            ''')
            
            columns = [desc[0] for desc in cursor.description]
            schedules = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 開始時間と終了時間が同じスケジュールを修正（1時間の枠に設定）
            updated_count = 0
            for schedule in schedules:
                start_time = schedule.get('start_time', '').replace('：', ':').replace('～', '-').replace('~', '-').strip()
                end_time = schedule.get('end_time', '').replace('：', ':').replace('～', '-').replace('~', '-').strip()
                
                # 開始時間と終了時間が同じ場合は1時間後に修正
                if start_time == end_time or not end_time:
                    try:
                        # 開始時間を解析（'-'が含まれている場合は削除）
                        start_time_clean = start_time.replace('-', '').strip()
                        if ':' in start_time_clean:
                            parts = start_time_clean.split(':')
                            hour = parts[0].strip()
                            minute = parts[1].strip() if len(parts) > 1 else '0'
                            hour_int = int(hour) if hour else 0
                            minute_int = int(minute) if minute else 0
                        else:
                            hour_int = int(start_time_clean) if start_time_clean else 0
                            minute_int = 0
                            start_time = f"{hour_int:02d}:{minute_int:02d}"
                        
                        # 1時間後の終了時間を計算
                        end_hour = hour_int + 1
                        new_end_time = f"{end_hour:02d}:{minute_int:02d}"
                        
                        # データベースを更新
                        schedule_id = schedule.get('id')
                        cursor.execute('''
                            UPDATE schedules 
                            SET end_time = ?
                            WHERE id = ?
                        ''', (new_end_time, schedule_id))
                        
                        # メモリ内のデータも更新
                        schedule['end_time'] = new_end_time
                        updated_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ スケジュール修正エラー（ID: {schedule.get('id')}）: {e}")
            
            if updated_count > 0:
                conn.commit()
                print(f"✅ {updated_count}個のスケジュールエントリを1時間の枠に修正しました")
            
        except Exception as e:
            print(f"get_weekly_schedule エラー: {e}")
            # テーブルが存在しない場合は空のリストを返す
            schedules = []
        finally:
            conn.close()
        
        return schedules
    
    # 未割り当てケース管理メソッド
    def add_unassigned_case(self, case_data):
        """未割り当てケースを追加（既に存在する場合は更新）"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        cursor = conn.cursor()
        
        try:
            # 既に同じケース番号が存在するかチェック
            cursor.execute('SELECT id FROM unassigned_cases WHERE case_number = ?', (case_data.get('case_number'),))
            existing = cursor.fetchone()
            
            if existing:
                # 既存のケースを更新
                cursor.execute('''
                    UPDATE unassigned_cases 
                    SET district = ?,
                        child_name = ?,
                        child_age = ?,
                        child_gender = ?,
                        preferred_day = ?,
                        preferred_time = ?,
                        frequency = ?,
                        location = ?,
                        notes = ?,
                        status = '未割り当て'
                    WHERE case_number = ?
                ''', (
                    case_data.get('district'),
                    case_data.get('child_name'),
                    case_data.get('child_age'),
                    case_data.get('child_gender'),
                    case_data.get('preferred_day'),
                    case_data.get('preferred_time'),
                    case_data.get('frequency'),
                    case_data.get('location'),
                    case_data.get('notes'),
                    case_data.get('case_number')
                ))
                case_id = existing[0]
            else:
                # 新規ケースを追加
                cursor.execute('''
                    INSERT INTO unassigned_cases 
                    (case_number, district, child_name, child_age, child_gender, 
                     preferred_day, preferred_time, frequency, location, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    case_data.get('case_number'),
                    case_data.get('district'),
                    case_data.get('child_name'),
                    case_data.get('child_age'),
                    case_data.get('child_gender'),
                    case_data.get('preferred_day'),
                    case_data.get('preferred_time'),
                    case_data.get('frequency'),
                    case_data.get('location'),
                    case_data.get('notes'),
                    '未割り当て'
                ))
                case_id = cursor.lastrowid
            
            conn.commit()
        finally:
            conn.close()
        
        return case_id
    
    def get_unassigned_cases(self):
        """未割り当てケース一覧を取得"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM unassigned_cases 
                WHERE status = '未割り当て'
                ORDER BY created_at DESC
            ''')
            columns = [desc[0] for desc in cursor.description]
            cases = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"get_unassigned_cases エラー: {e}")
            cases = []
        finally:
            conn.close()
        
        return cases
    
    def assign_case_to_staff(self, case_id, staff_id):
        """ケースを支援員に割り当て"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # ケース情報を取得
            cursor.execute('SELECT * FROM unassigned_cases WHERE id = ?', (case_id,))
            case = cursor.fetchone()
            
            if not case:
                raise ValueError("ケースが見つかりません")
            
            # 支援員にケースを追加
            cursor.execute('''
                INSERT INTO staff (name, age, gender, region, work_days, work_hours, 
                                case_district, case_number, case_day, case_time, case_frequency, case_location)
                SELECT name, age, gender, region, preferred_day, preferred_time,
                       district, case_number, preferred_day, preferred_time, frequency, location
                FROM unassigned_cases
                WHERE id = ?
            ''')
            
            # ケースを割り当て済みに変更
            cursor.execute('''
                UPDATE unassigned_cases 
                SET status = '割り当て済み' 
                WHERE id = ?
            ''', (case_id,))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def assign_unassigned_case_to_staff(self, unassigned_case_id, staff_id):
        """未割り当てケースを支援員に割り当て"""
        import time
        
        max_retries = 5
        retry_delay = 0.2
        
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(str(self.db_path), timeout=10.0)
                cursor = conn.cursor()
                
                # 未割り当てケース情報を取得
                cursor.execute('SELECT * FROM unassigned_cases WHERE id = ?', (unassigned_case_id,))
                columns = [desc[0] for desc in cursor.description]
                case = dict(zip(columns, cursor.fetchone()))
                
                if not case:
                    raise ValueError("ケースが見つかりません")
                
                # 支援員のケース情報を更新
                cursor.execute('''
                    UPDATE staff 
                    SET case_district = ?,
                        case_number = ?,
                        case_day = ?,
                        case_time = ?,
                        case_frequency = ?,
                        case_location = ?
                    WHERE id = ?
                ''', (
                    case.get('district'),
                    case.get('case_number'),
                    case.get('preferred_day'),
                    case.get('preferred_time'),
                    case.get('frequency', '未設定'),
                    case.get('location'),
                    staff_id
                ))
                
                # ケースを割り当て済みに変更
                cursor.execute('''
                    UPDATE unassigned_cases 
                    SET status = '割り当て済み' 
                    WHERE id = ?
                ''', (unassigned_case_id,))
                
                conn.commit()
                conn.close()
                break
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise e

    def get_staff_by_id(self, staff_id):
        """IDで支援員を取得"""
        if not staff_id:
            return None
            
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # staff_idを整数に変換
            staff_id_int = int(staff_id)
            cursor.execute('SELECT * FROM staff WHERE id = ?', (staff_id_int,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            
            if row:
                staff = dict(zip(columns, row))
            else:
                staff = None
        except (ValueError, TypeError) as e:
            print(f"get_staff_by_id エラー: staff_idが無効です - {staff_id}: {e}")
            staff = None
        except Exception as e:
            print(f"get_staff_by_id エラー: {e}")
            staff = None
        finally:
            conn.close()
        
        return staff
