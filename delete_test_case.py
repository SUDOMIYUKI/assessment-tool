#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""城東区のテストケースを削除するスクリプト"""
import sqlite3
from pathlib import Path

db_path = Path('data/records.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 城東区のケースを確認
cursor.execute('''
    SELECT c.id, c.case_number, d.name as district_name, c.child_name
    FROM cases c
    JOIN districts d ON c.district_id = d.id
    WHERE d.name = ?
''', ('城東区',))

cases = cursor.fetchall()
print(f"城東区のケース: {len(cases)}件見つかりました")
for case in cases:
    print(f"  - ID: {case[0]}, ケース番号: {case[1]}, 児童名: {case[3]}")

if cases:
    # 城東区のケースIDを取得
    case_ids = [case[0] for case in cases]
    
    # 関連するスケジュールエントリを削除
    for case_id in case_ids:
        cursor.execute('DELETE FROM schedules WHERE case_id = ?', (case_id,))
        print(f"  ケースID {case_id} のスケジュールエントリを削除しました")
    
    # 関連するstaff_casesエントリを削除
    for case_id in case_ids:
        cursor.execute('DELETE FROM staff_cases WHERE case_id = ?', (case_id,))
        print(f"  ケースID {case_id} のstaff_casesエントリを削除しました")
    
    # ケースを削除
    for case_id in case_ids:
        cursor.execute('DELETE FROM cases WHERE id = ?', (case_id,))
        print(f"  ケースID {case_id} を削除しました")
    
    conn.commit()
    print(f"\n✅ {len(cases)}件のケースを削除しました")
else:
    print("削除するケースが見つかりませんでした")

conn.close()
