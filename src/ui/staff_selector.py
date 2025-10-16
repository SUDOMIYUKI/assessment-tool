import tkinter as tk
from tkinter import ttk, messagebox
from src.database.staff import StaffManager

class StaffSelectorDialog(tk.Toplevel):
    def __init__(self, parent, support_wishes=None):
        super().__init__(parent)
        
        self.staff_manager = StaffManager()
        self.selected_staff = None
        self.support_wishes = support_wishes or {}
        
        self.title("支援員選択")
        self.geometry("1000x650")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.search_staff()
        
        # 中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        # ヘッダー
        header_frame = tk.Frame(self, bg="#3498db", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="👥 支援員選択",
            font=("游ゴシック", 14, "bold"),
            bg="#3498db",
            fg="white"
        )
        title.pack(pady=15)
        
        # 検索条件エリア
        search_frame = ttk.LabelFrame(self, text="検索条件", padding=10)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # 1行目
        row1 = tk.Frame(search_frame)
        row1.pack(fill="x", pady=2)
        
        tk.Label(row1, text="希望地域:", font=("游ゴシック", 10)).pack(side="left", padx=(0, 5))
        self.region_var = tk.StringVar()
        self.region_combo = ttk.Combobox(row1, textvariable=self.region_var, width=15, state="readonly")
        self.region_combo.pack(side="left", padx=(0, 20))
        
        tk.Label(row1, text="性別:", font=("游ゴシック", 10)).pack(side="left", padx=(0, 5))
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(row1, textvariable=self.gender_var, values=["", "男性", "女性"], width=8, state="readonly")
        self.gender_combo.pack(side="left", padx=(0, 20))
        
        tk.Label(row1, text="年齢範囲:", font=("游ゴシック", 10)).pack(side="left", padx=(0, 5))
        self.age_from_var = tk.StringVar()
        self.age_to_var = tk.StringVar()
        self.age_from_combo = ttk.Combobox(row1, textvariable=self.age_from_var, values=["", "20", "25", "30", "35", "40", "45", "50"], width=5, state="readonly")
        self.age_from_combo.pack(side="left", padx=(0, 2))
        tk.Label(row1, text="〜").pack(side="left")
        self.age_to_combo = ttk.Combobox(row1, textvariable=self.age_to_var, values=["", "25", "30", "35", "40", "45", "50", "55"], width=5, state="readonly")
        self.age_to_combo.pack(side="left", padx=(2, 0))
        
        # 2行目
        row2 = tk.Frame(search_frame)
        row2.pack(fill="x", pady=2)
        
        tk.Label(row2, text="希望曜日:", font=("游ゴシック", 10)).pack(side="left", padx=(0, 5))
        self.preferred_days_frame = tk.Frame(row2)
        self.preferred_days_frame.pack(side="left", padx=(0, 20))
        
        # 希望曜日のチェックボックス
        self.preferred_days_vars = {}
        days = ['月', '火', '水', '木', '金']
        for i, day in enumerate(days):
            self.preferred_days_vars[day] = tk.BooleanVar()
            ttk.Checkbutton(
                self.preferred_days_frame, 
                text=day, 
                variable=self.preferred_days_vars[day]
            ).pack(side="left", padx=2)
        
        tk.Label(row2, text="希望時間:", font=("游ゴシック", 10)).pack(side="left", padx=(0, 5))
        self.preferred_time_frame = tk.Frame(row2)
        self.preferred_time_frame.pack(side="left", padx=(0, 20))
        
        # 希望開始時間
        tk.Label(self.preferred_time_frame, text="開始:", font=("游ゴシック", 9)).pack(side="left", padx=(0, 2))
        self.preferred_start_var = tk.StringVar()
        self.preferred_start_entry = ttk.Entry(self.preferred_time_frame, textvariable=self.preferred_start_var, width=6)
        self.preferred_start_entry.pack(side="left", padx=(0, 5))
        
        # 希望終了時間
        tk.Label(self.preferred_time_frame, text="終了:", font=("游ゴシック", 9)).pack(side="left", padx=(0, 2))
        self.preferred_end_var = tk.StringVar()
        self.preferred_end_entry = ttk.Entry(self.preferred_time_frame, textvariable=self.preferred_end_var, width=6)
        self.preferred_end_entry.pack(side="left")
        
        search_btn = tk.Button(
            row2,
            text="🔍 検索",
            font=("游ゴシック", 10),
            bg="#3498db",
            fg="white",
            command=self.search_staff,
            padx=15,
            pady=5
        )
        search_btn.pack(side="left")
        
        # 3行目
        row3 = tk.Frame(search_frame)
        row3.pack(fill="x", pady=2)
        
        tk.Label(row3, text="趣味・特技:", font=("游ゴシック", 10)).pack(side="left", padx=(0, 5))
        self.interests_var = tk.StringVar()
        self.interests_entry = ttk.Entry(row3, textvariable=self.interests_var, width=30)
        self.interests_entry.pack(side="left", padx=(0, 10))
        
        # 支援員一覧
        list_frame = ttk.LabelFrame(self, text="支援員一覧", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ツリービュー（表形式）
        columns = ('name', 'age', 'gender', 'region', 'work_days', 'work_hours', 'hobbies_skills', 'dropbox')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 列の設定
        self.tree.heading('name', text='名前')
        self.tree.heading('age', text='年齢')
        self.tree.heading('gender', text='性別')
        self.tree.heading('region', text='地域')
        self.tree.heading('work_days', text='勤務曜日')
        self.tree.heading('work_hours', text='勤務時間')
        self.tree.heading('hobbies_skills', text='趣味・特技')
        self.tree.heading('dropbox', text='Dropbox')
        
        # 列幅の設定
        self.tree.column('name', width=80)
        self.tree.column('age', width=50)
        self.tree.column('gender', width=60)
        self.tree.column('region', width=100)
        self.tree.column('work_days', width=80)
        self.tree.column('work_hours', width=100)
        self.tree.column('hobbies_skills', width=120)
        self.tree.column('dropbox', width=80)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 選択イベント
        self.tree.bind('<<TreeviewSelect>>', self.on_staff_selected)
        
        # ボタンエリア
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ キャンセル",
            font=("游ゴシック", 11),
            bg="#e74c3c",
            fg="white",
            command=self.destroy,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side="left")
        
        select_btn = tk.Button(
            button_frame,
            text="✅ この支援員を選択",
            font=("游ゴシック", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.select_staff,
            padx=20,
            pady=8,
            state="disabled"
        )
        select_btn.pack(side="right")
        self.select_btn = select_btn
        
        # 地域リストを初期化
        self.init_region_list()
    
    def init_region_list(self):
        """地域リストを初期化"""
        regions = []
        for staff in self.staff_manager.get_all_staff():
            region = staff['region']
            if region and region not in regions:
                regions.append(region)
        regions.sort()
        self.region_combo['values'] = [''] + regions
    
    def search_staff(self):
        """支援員を検索"""
        # 検索条件を取得
        preferred_region = self.region_var.get() if self.region_var.get() else None
        gender_preference = self.gender_var.get() if self.gender_var.get() else None
        
        # 年齢範囲
        age_range = None
        if self.age_from_var.get() and self.age_to_var.get():
            try:
                age_from = int(self.age_from_var.get())
                age_to = int(self.age_to_var.get())
                age_range = (age_from, age_to)
            except ValueError:
                pass
        
        # 勤務曜日
        preferred_days = []
        for day, var in self.preferred_days_vars.items():
            if var.get():
                preferred_days.append(day)
        preferred_day = preferred_days if preferred_days else None
        
        # 勤務時間
        start_time = self.preferred_start_var.get().strip()
        end_time = self.preferred_end_var.get().strip()
        preferred_time = f"{start_time}-{end_time}" if start_time and end_time else None
        
        # 趣味・特技
        interests = []
        if self.interests_var.get():
            interests = [interest.strip() for interest in self.interests_var.get().split(',')]
        
        # 検索条件をデバッグ出力
        print("🔍 検索条件:")
        print(f"  地域: {preferred_region or '指定なし'}")
        print(f"  年齢範囲: {age_range or '指定なし'}")
        print(f"  性別: {gender_preference or '指定なし'}")
        print(f"  希望曜日: {preferred_day or '指定なし'}")
        print(f"  希望時間: {preferred_time or '指定なし'}")
        print(f"  趣味・特技: {interests or '指定なし'}")
        
        # 検索実行
        staff_list = self.staff_manager.search_matching_staff(
            preferred_region=preferred_region,
            age_range=age_range,
            gender_preference=gender_preference,
            preferred_day=preferred_day,
            preferred_time=preferred_time,
            interests=interests
        )
        
        # 検索条件が何も設定されていない場合は全支援員を表示
        if not any([preferred_region, age_range, gender_preference, preferred_day, preferred_time, interests]):
            staff_list = self.staff_manager.get_all_staff()
            print("📋 検索条件なし: 全支援員を表示")
        
        # 結果を表示
        self.display_staff_list(staff_list)
    
    def display_staff_list(self, staff_list):
        """支援員リストを表示"""
        # 既存のアイテムをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 検索結果の件数を表示
        result_count = len(staff_list)
        print(f"🔍 検索結果: {result_count}名の支援員が見つかりました")
        
        if result_count == 0:
            # 検索結果が0件の場合、条件を緩和した検索を提案
            self.show_search_suggestions()
        
        # 新しいアイテムを追加
        for staff in staff_list:
            self.tree.insert('', 'end', values=(
                staff['name'],
                staff['age'],
                staff['gender'],
                staff['region'],
                staff['work_days'] or '',
                staff['work_hours'] or '',
                staff['hobbies_skills'] or '',
                staff['dropbox_number'] or ''
            ), tags=(staff['id'],))
    
    def show_search_suggestions(self):
        """検索結果が0件の場合の提案を表示"""
        print("💡 検索条件を緩和する提案:")
        print("   - 曜日条件を減らす（例：月曜日のみ → 月火水木金のいずれか）")
        print("   - 時間帯を広げる（例：14:00-15:00 → 13:00-17:00）")
        print("   - 地域条件を削除")
        print("   - 年齢範囲を広げる")
        print("   - 性別条件を削除")
    
    def on_staff_selected(self, event):
        """支援員が選択された時"""
        selection = self.tree.selection()
        if selection:
            self.select_btn.config(state="normal")
        else:
            self.select_btn.config(state="disabled")
    
    def select_staff(self):
        """支援員を選択"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "支援員を選択してください")
            return
        
        item = self.tree.item(selection[0])
        staff_id = item['tags'][0]
        
        self.selected_staff = self.staff_manager.get_staff_by_id(staff_id)
        self.destroy()
    
    def get_selected_staff(self):
        """選択された支援員を取得"""
        return self.selected_staff
