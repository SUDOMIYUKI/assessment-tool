import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
import pyperclip
from pathlib import Path

class PlaceholderCombobox(ttk.Combobox):
    """プレースホルダー機能付きComboboxウィジェット"""
    def __init__(self, parent, placeholder="", options=None, **kwargs):
        # Comboboxの初期化
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.options = options or []
        self.placeholder_color = "gray"
        self.normal_color = "black"
        self.is_placeholder = True
        
        # 候補を設定
        if self.options:
            self['values'] = self.options
        
        # プレースホルダーテキストを表示（setメソッドを使わず直接設定）
        if placeholder:
            super().set(placeholder)
            self.config(foreground=self.placeholder_color)
        
        # イベントバインド
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<<ComboboxSelected>>", self._on_selection_changed)
    
    def _on_focus_in(self, event):
        if self.is_placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.normal_color)
            self.is_placeholder = False
            # フォーカス取得時にテキストを全選択
            self.selection_range(0, tk.END)
    
    def _on_focus_out(self, event):
        current_value = super().get()  # プレースホルダー状態を無視して実際の値を取得
        if not current_value.strip() and self.placeholder:
            super().set(self.placeholder)
            self.config(foreground=self.placeholder_color)
            self.is_placeholder = True
    
    def _on_key_press(self, event):
        if self.is_placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.normal_color)
            self.is_placeholder = False
    
    def _on_selection_changed(self, event):
        """ドロップダウンから選択された時"""
        self.config(foreground=self.normal_color)
        self.is_placeholder = False
    
    def get(self):
        """値を取得（プレースホルダーの場合は空文字を返す）"""
        if self.is_placeholder:
            return ""
        return super().get()
    
    def set(self, value):
        """値を設定"""
        if value and value != self.placeholder:
            super().set(value)
            self.config(foreground=self.normal_color)
            self.is_placeholder = False
        elif not value and self.placeholder:
            super().set(self.placeholder)
            self.config(foreground=self.placeholder_color)
            self.is_placeholder = True

class PlaceholderTextArea:
    """プレースホルダー機能付きテキストエリア（複数行対応）"""
    def __init__(self, parent, placeholder="", options=None, **kwargs):
        self.frame = tk.Frame(parent)
        self.placeholder = placeholder
        self.options = options or []
        self.placeholder_color = "gray"
        self.normal_color = "black"
        self.is_placeholder = True
        
        # テキストエリアを作成
        self.text_widget = scrolledtext.ScrolledText(self.frame, **kwargs)
        self.text_widget.pack(side="top", fill="both", expand=True)
        
        # ScrolledText内部のTextウィジェットにアクセス
        # ScrolledTextはFrameを継承しており、内部にTextウィジェットを持つ
        self.inner_text = None
        for child in self.text_widget.winfo_children():
            if isinstance(child, tk.Text):
                self.inner_text = child
                break
        
        # もし見つからない場合は、ScrolledText自体を使用
        if self.inner_text is None:
            self.inner_text = self.text_widget
        
        # ドロップダウンボタンを追加（テキストエリアの下に配置）
        if self.options:
            self.combo_frame = tk.Frame(self.frame)
            self.combo_frame.pack(side="top", fill="x", pady=(5, 0))
            ttk.Label(self.combo_frame, text="例から選択:", font=("游ゴシック", 9)).pack(side="left", padx=(0, 5))
            self.combo = ttk.Combobox(self.combo_frame, values=self.options, width=50, state="readonly", font=("游ゴシック", 9))
            self.combo.pack(side="left", fill="x", expand=True)
            self.combo.bind("<<ComboboxSelected>>", self._on_option_selected)
        else:
            self.combo = None
        
        # プレースホルダーテキストを表示
        if placeholder:
            self.text_widget.insert("1.0", placeholder)
            self.inner_text.config(foreground=self.placeholder_color)
        
        # イベントバインド
        self.inner_text.bind("<FocusIn>", self._on_focus_in)
        self.inner_text.bind("<FocusOut>", self._on_focus_out)
        self.inner_text.bind("<KeyPress>", self._on_key_press)
        self.inner_text.bind("<Button-1>", self._on_click)
    
    def _on_focus_in(self, event):
        if self.is_placeholder:
            self.text_widget.delete("1.0", tk.END)
            self.inner_text.config(foreground=self.normal_color)
            self.is_placeholder = False
    
    def _on_focus_out(self, event):
        current_value = self.text_widget.get("1.0", tk.END).strip()
        if not current_value and self.placeholder:
            self.text_widget.insert("1.0", self.placeholder)
            self.inner_text.config(foreground=self.placeholder_color)
            self.is_placeholder = True
    
    def _on_key_press(self, event):
        if self.is_placeholder:
            self.text_widget.delete("1.0", tk.END)
            self.inner_text.config(foreground=self.normal_color)
            self.is_placeholder = False
    
    def _on_click(self, event):
        if self.is_placeholder:
            self.text_widget.delete("1.0", tk.END)
            self.inner_text.config(foreground=self.normal_color)
            self.is_placeholder = False
    
    def _on_option_selected(self, event):
        """ドロップダウンから選択された時"""
        selected = self.combo.get()
        if selected:
            # 選択値をそのまま挿入（選択肢には既に「例：」が含まれていない）
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", selected)
            self.inner_text.config(foreground=self.normal_color)
            self.is_placeholder = False
    
    def get(self):
        """値を取得（プレースホルダーの場合は空文字を返す）"""
        if self.is_placeholder:
            return ""
        return self.text_widget.get("1.0", tk.END).strip()
    
    def grid(self, **kwargs):
        """grid配置"""
        return self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """pack配置"""
        return self.frame.pack(**kwargs)
    
    def bind(self, event, handler):
        """イベントバインド"""
        return self.text_widget.bind(event, handler)

class SmartInputForm(tk.Toplevel):
    """スマート入力フォーム - 構造化された入力で即座にアセスメント完成"""
    
    def __init__(self, parent, on_complete_callback):
        super().__init__(parent)
        self.on_complete_callback = on_complete_callback
        self.parent = parent
        
        self.title("⚡ スマート面談記録")
        self.geometry("1000x800")
        
        # 中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
        
        # モーダル設定
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        # タイトル
        title = tk.Label(
            self,
            text="⚡ スマート面談記録（リアルタイム作成）",
            font=("游ゴシック", 18, "bold")
        )
        title.pack(pady=10)
        
        hint = tk.Label(
            self,
            text="💡 面談しながらチェック・入力するだけで、アセスメントシートと報告書が同時に完成します",
            font=("游ゴシック", 10),
            fg="gray"
        )
        hint.pack(pady=5)
        
        # スクロール可能なキャンバス
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # === セクション1：基本情報 ===
        basic_frame = ttk.LabelFrame(scrollable_frame, text="📋 基本情報", padding=15)
        basic_frame.pack(fill="x", padx=20, pady=10)
        
        row = 0
        ttk.Label(basic_frame, text="児童氏名:").grid(row=row, column=0, sticky="w", pady=5)
        self.child_name_entry = ttk.Entry(basic_frame, width=20)
        self.child_name_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="性別:").grid(row=row, column=2, sticky="w", padx=(20, 5))
        self.gender_var = tk.StringVar(value="男性")
        ttk.Radiobutton(basic_frame, text="男性", variable=self.gender_var, value="男性").grid(row=row, column=3, sticky="w")
        ttk.Radiobutton(basic_frame, text="女性", variable=self.gender_var, value="女性").grid(row=row, column=4, sticky="w")
        
        row += 1
        ttk.Label(basic_frame, text="保護者氏名:").grid(row=row, column=0, sticky="w", pady=5)
        self.guardian_name_entry = ttk.Entry(basic_frame, width=20)
        self.guardian_name_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        row += 1
        ttk.Label(basic_frame, text="学校名:").grid(row=row, column=0, sticky="w", pady=5)
        self.school_entry = ttk.Entry(basic_frame, width=30)
        self.school_entry.grid(row=row, column=1, columnspan=2, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="学年:").grid(row=row, column=3, sticky="w", padx=(20, 5))
        self.grade_spinbox = ttk.Spinbox(basic_frame, from_=1, to=12, width=5)
        self.grade_spinbox.set("2")
        self.grade_spinbox.grid(row=row, column=4, sticky="w")
        
        row += 1
        ttk.Label(basic_frame, text="担当支援員:").grid(row=row, column=0, sticky="w", pady=5)
        self.supporter_entry = ttk.Entry(basic_frame, width=20)
        self.supporter_entry.grid(row=row, column=1, sticky="w", padx=5)
        
        ttk.Label(basic_frame, text="面談実施日:").grid(row=row, column=2, sticky="w", padx=(20, 5))
        self.interview_date_entry = ttk.Entry(basic_frame, width=15)
        self.interview_date_entry.insert(0, datetime.now().strftime('%Y/%m/%d'))
        self.interview_date_entry.grid(row=row, column=3, columnspan=2, sticky="w")
        
        row += 1
        ttk.Label(basic_frame, text="家族構成:").grid(row=row, column=0, sticky="w", pady=5)
        self.family_structure_entry = PlaceholderCombobox(
            basic_frame, 
            width=47,
            placeholder="例：父・母・本人・妹",
            options=[
                "父・母・本人・妹",
                "父・母・本人・兄",
                "母・本人・妹",
                "父・本人・兄・妹",
                "母・本人"
            ]
        )
        self.family_structure_entry.grid(row=row, column=1, columnspan=4, sticky="w", padx=5)
        
        row += 1
        ttk.Label(basic_frame, text="本人の趣味・好きなこと:").grid(row=row, column=0, sticky="w", pady=5)
        self.hobbies_entry = PlaceholderCombobox(
            basic_frame, 
            width=47,
            placeholder="例：ゲーム、YouTube視聴、イラスト",
            options=[
                "ゲーム、YouTube視聴、イラスト",
                "ゲーム、アニメ、音楽",
                "スポーツ、ゲーム、読書",
                "イラスト、動画編集、音楽",
                "読書、ゲーム、友達と遊ぶ"
            ]
        )
        self.hobbies_entry.grid(row=row, column=1, columnspan=4, sticky="w", padx=5)
        
        # === セクション2：登校状況 ===
        attendance_frame = ttk.LabelFrame(scrollable_frame, text="🏫 登校状況", padding=15)
        attendance_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(attendance_frame, text="現在の登校頻度:").grid(row=0, column=0, sticky="w", pady=5)
        self.attendance_var = tk.StringVar(value="週0回")
        attendance_options = ["週0回（完全不登校）", "週1-2回", "週3-4回", "ほぼ毎日"]
        self.attendance_combo = ttk.Combobox(attendance_frame, textvariable=self.attendance_var, values=attendance_options, width=25)
        self.attendance_combo.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(attendance_frame, text="不登校の状況:").grid(row=1, column=0, sticky="nw", pady=5)
        self.truancy_check = tk.BooleanVar()
        ttk.Checkbutton(attendance_frame, text="不登校に該当", variable=self.truancy_check).grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(attendance_frame, text="詳細・経緯:").grid(row=2, column=0, sticky="nw", pady=5)
        self.truancy_detail = PlaceholderTextArea(
            attendance_frame,
            width=50,
            height=3,
            wrap=tk.WORD,
            placeholder="例：転校してから不登校が始まった、友達関係の問題が原因",
            options=[
                "転校してから不登校が始まった、友達関係の問題が原因",
                "いじめが原因で不登校になった",
                "朝起きられず、学校に行けなくなった",
                "学業不振が原因で学校に行きたくない",
                "人間関係がうまくいかず、学校に行けなくなった"
            ]
        )
        self.truancy_detail.grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
        
        # マウスホイールでテキストエリア内スクロール
        def _on_truancy_mousewheel(event):
            self.truancy_detail.text_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        self.truancy_detail.inner_text.bind("<MouseWheel>", _on_truancy_mousewheel)
        
        # === セクション3：生活状況 ===
        life_frame = ttk.LabelFrame(scrollable_frame, text="🏠 生活状況", padding=15)
        life_frame.pack(fill="x", padx=20, pady=10)
        
        # 生活リズム
        ttk.Label(life_frame, text="生活リズムの課題:").grid(row=0, column=0, sticky="nw", pady=5)
        rhythm_frame = tk.Frame(life_frame)
        rhythm_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        self.rhythm_checks = {}
        rhythm_items = ["朝起きられない", "昼夜逆転", "睡眠不足", "特に問題なし"]
        for i, item in enumerate(rhythm_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(rhythm_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.rhythm_checks[item] = var
        
        ttk.Label(life_frame, text="生活リズムの詳細:").grid(row=1, column=0, sticky="nw", pady=5)
        self.rhythm_detail = PlaceholderCombobox(
            life_frame, 
            width=57,
            placeholder="例：昼夜逆転で午後2時起床、夜中3時就寝",
            options=[
                "昼夜逆転で午後2時起床、夜中3時就寝",
                "朝起きられず午前11時起床、夜中2時就寝",
                "睡眠不足で5時間程度の睡眠",
                "不規則な生活リズム",
                "特に問題なし"
            ]
        )
        self.rhythm_detail.grid(row=1, column=1, sticky="w", padx=5)
        
        # 生活習慣
        ttk.Label(life_frame, text="生活習慣の課題:").grid(row=2, column=0, sticky="nw", pady=5)
        habit_frame = tk.Frame(life_frame)
        habit_frame.grid(row=2, column=1, sticky="w", padx=5)
        
        self.habit_checks = {}
        habit_items = ["食事の乱れ", "運動不足", "ゲーム依存傾向", "特に問題なし"]
        for i, item in enumerate(habit_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(habit_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.habit_checks[item] = var
        
        ttk.Label(life_frame, text="生活習慣の詳細:").grid(row=3, column=0, sticky="nw", pady=5)
        self.habit_detail = PlaceholderCombobox(
            life_frame, 
            width=57,
            placeholder="例：1日1食、ゲームを10時間以上",
            options=[
                "1日1食、ゲームを10時間以上",
                "食事の時間が不規則、運動不足",
                "ゲーム依存、昼夜逆転",
                "偏食、睡眠不足",
                "特に問題なし"
            ]
        )
        self.habit_detail.grid(row=3, column=1, sticky="w", padx=5)
        
        # 引きこもり
        ttk.Label(life_frame, text="外出状況:").grid(row=4, column=0, sticky="w", pady=5)
        self.outing_var = tk.StringVar(value="外出する")
        outing_options = ["外出する", "コンビニ程度", "ほぼ外出しない"]
        self.outing_combo = ttk.Combobox(life_frame, textvariable=self.outing_var, values=outing_options, width=20)
        self.outing_combo.grid(row=4, column=1, sticky="w", padx=5)
        
        # === セクション4：学習状況 ===
        study_frame = ttk.LabelFrame(scrollable_frame, text="📚 学習状況", padding=15)
        study_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(study_frame, text="学習の課題:").grid(row=0, column=0, sticky="nw", pady=5)
        study_issues_frame = tk.Frame(study_frame)
        study_issues_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        self.study_checks = {}
        study_items = ["学習の遅れ", "低学力", "学習習慣なし", "学習環境なし", "特に問題なし"]
        for i, item in enumerate(study_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(study_issues_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.study_checks[item] = var
        
        ttk.Label(study_frame, text="学習の詳細:").grid(row=1, column=0, sticky="nw", pady=5)
        self.study_detail = PlaceholderCombobox(
            study_frame, 
            width=57,
            placeholder="例：小学生の勉強ができておらず、板書が全くできない",
            options=[
                "小学生の勉強ができておらず、板書が全くできない",
                "授業についていけず、宿題もできていない",
                "学習習慣がなく、集中力が続かない",
                "学習環境が整っておらず、勉強する場所がない",
                "特に問題なし"
            ]
        )
        self.study_detail.grid(row=1, column=1, sticky="w", padx=5)
        
        # === セクション5：対人関係 ===
        social_frame = ttk.LabelFrame(scrollable_frame, text="👥 対人関係・コミュニケーション", padding=15)
        social_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(social_frame, text="対人関係の課題:").grid(row=0, column=0, sticky="nw", pady=5)
        social_issues_frame = tk.Frame(social_frame)
        social_issues_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        self.social_checks = {}
        social_items = ["対人緊張が高い", "友達との関わりに不安", "コミュニケーション苦手", "特に問題なし"]
        for i, item in enumerate(social_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(social_issues_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.social_checks[item] = var
        
        ttk.Label(social_frame, text="対人関係の詳細:").grid(row=1, column=0, sticky="nw", pady=5)
        self.social_detail = PlaceholderCombobox(
            social_frame, 
            width=57,
            placeholder="例：初回面談時、目線が合いにくく緊張している様子",
            options=[
                "初回面談時、目線が合いにくく緊張している様子",
                "友達との関係に不安を感じている",
                "コミュニケーションが苦手で話しかけにくい",
                "集団行動が苦手で一人でいることが多い",
                "特に問題なし"
            ]
        )
        self.social_detail.grid(row=1, column=1, sticky="w", padx=5)
        
        # === セクション6：発達特性 ===
        dev_frame = ttk.LabelFrame(scrollable_frame, text="🧠 発達特性・医療情報", padding=15)
        dev_frame.pack(fill="x", padx=20, pady=10)
        
        self.dev_check_var = tk.BooleanVar()
        ttk.Checkbutton(dev_frame, text="発達特性または発達課題あり", variable=self.dev_check_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(dev_frame, text="詳細:").grid(row=1, column=0, sticky="w", pady=5)
        self.dev_detail = PlaceholderCombobox(
            dev_frame, 
            width=47,
            placeholder="例：注意散漫、集中力不足",
            options=[
                "注意散漫、集中力不足",
                "コミュニケーションの困難",
                "学習の遅れ、理解の困難",
                "感覚過敏、感覚鈍麻",
                "その他"
            ]
        )
        self.dev_detail.grid(row=1, column=1, sticky="w", padx=5)
        
        self.medical_check_var = tk.BooleanVar(value=False)
        medical_check = ttk.Checkbutton(
            dev_frame,
            text="通院あり",
            variable=self.medical_check_var,
            command=self.toggle_medical_fields
        )
        medical_check.grid(row=2, column=0, sticky="w", pady=5)
        
        self.medical_detail_frame = ttk.Frame(dev_frame)
        self.medical_detail_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        self.medical_detail_frame.grid_remove()
        
        ttk.Label(self.medical_detail_frame, text="病院名:").grid(row=0, column=0, sticky="w", pady=3)
        self.hospital_entry = PlaceholderCombobox(
            self.medical_detail_frame, 
            width=27,
            placeholder="例：○○病院",
            options=[
                "○○病院",
                "○○クリニック",
                "○○メンタルクリニック",
                "○○小児科",
                "その他"
            ]
        )
        self.hospital_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(self.medical_detail_frame, text="頻度:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.frequency_entry = PlaceholderCombobox(
            self.medical_detail_frame, 
            width=12,
            placeholder="例：月1回",
            options=[
                "月1回",
                "月2回",
                "週1回",
                "隔週1回",
                "不定期"
            ]
        )
        self.frequency_entry.grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(self.medical_detail_frame, text="診断名:").grid(row=1, column=0, sticky="w", pady=3)
        self.diagnosis_entry = PlaceholderCombobox(
            self.medical_detail_frame, 
            width=27,
            placeholder="例：ADHD",
            options=[
                "ADHD",
                "ASD",
                "LD",
                "うつ病",
                "その他"
            ]
        )
        self.diagnosis_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(self.medical_detail_frame, text="投薬治療:").grid(row=2, column=0, sticky="w", pady=3)
        self.medication_entry = PlaceholderCombobox(
            self.medical_detail_frame, 
            width=27,
            placeholder="例：なし / 薬名",
            options=[
                "なし",
                "コンサータ",
                "ストラテラ",
                "リタリン",
                "その他"
            ]
        )
        self.medication_entry.grid(row=2, column=1, sticky="w", padx=5)
        
        ttk.Label(self.medical_detail_frame, text="手帳:").grid(row=2, column=2, sticky="w", padx=(20, 5))
        self.handbook_entry = PlaceholderCombobox(
            self.medical_detail_frame, 
            width=12,
            placeholder="例：なし / 種類",
            options=[
                "なし",
                "療育手帳B1",
                "療育手帳B2",
                "精神障害者手帳",
                "その他"
            ]
        )
        self.handbook_entry.grid(row=2, column=3, sticky="w", padx=5)
        
        # === セクション7：家庭環境 ===
        family_frame = ttk.LabelFrame(scrollable_frame, text="👨‍👩‍👧‍👦 家庭環境", padding=15)
        family_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(family_frame, text="ひとり親世帯:").grid(row=0, column=0, sticky="w", pady=5)
        self.single_parent_var = tk.StringVar(value="該当しない")
        ttk.Radiobutton(family_frame, text="該当", variable=self.single_parent_var, value="該当").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(family_frame, text="該当しない", variable=self.single_parent_var, value="該当しない").grid(row=0, column=2, sticky="w")
        
        ttk.Label(family_frame, text="家庭環境の課題:").grid(row=1, column=0, sticky="nw", pady=5)
        family_issues_frame = tk.Frame(family_frame)
        family_issues_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
        
        self.family_checks = {}
        family_items = ["経済的困難", "家族関係の課題", "他の世帯員の問題", "虐待", "その他", "特に問題なし"]
        for i, item in enumerate(family_items):
            var = tk.BooleanVar()
            ttk.Checkbutton(family_issues_frame, text=item, variable=var).grid(row=i//2, column=i%2, sticky="w", padx=5)
            self.family_checks[item] = var
        
        ttk.Label(family_frame, text="家庭環境の詳細:").grid(row=2, column=0, sticky="nw", pady=5)
        self.family_detail = PlaceholderCombobox(
            family_frame, 
            width=57,
            placeholder="例：弟が療育手帳B2、家庭内で暴言・暴力、父親との関係性が悪い",
            options=[
                "弟が療育手帳B2、家庭内で暴言・暴力、父親との関係性が悪い",
                "経済的困難で生活が苦しい",
                "家族関係が複雑で緊張状態",
                "他の世帯員に問題があり、本人に影響",
                "特に問題なし"
            ]
        )
        self.family_detail.grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
        
        # === セクション8：ニーズ・目標（短期・長期） ===
        needs_frame = ttk.LabelFrame(scrollable_frame, text="🎯 ニーズ・目標・支援計画", padding=15)
        needs_frame.pack(fill="x", padx=20, pady=10)
        
        # 短期目標セクション
        ttk.Label(needs_frame, text="<短期目標>", font=("游ゴシック", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # 課題
        ttk.Label(needs_frame, text="課題:").grid(row=1, column=0, sticky="nw", pady=5)
        self.short_term_issue = PlaceholderCombobox(
            needs_frame, 
            width=27,
            placeholder="例：学習の遅れ",
            options=[
                "学習の遅れ",
                "生活リズムの乱れ",
                "対人関係の課題",
                "家庭環境の問題",
                "発達特性への対応"
            ]
        )
        self.short_term_issue.grid(row=1, column=1, sticky="w", padx=5)
        
        # 現状
        ttk.Label(needs_frame, text="現状:").grid(row=2, column=0, sticky="nw", pady=5)
        self.short_term_current = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：小学生の勉強ができておらず、板書が全くできない。本人は半ば諦めている状態。",
            options=[
                "小学生の勉強ができておらず、板書が全くできない。本人は半ば諦めている状態。",
                "授業についていけず、宿題もできていない。学習に対する自信を失っている。",
                "学習習慣がなく、集中力が続かない。勉強する場所も整っていない。",
                "学習環境が整っておらず、家族からのサポートも不足している。",
                "特に問題はないが、学習意欲を高めたい状況。"
            ]
        )
        self.short_term_current.grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
        
        # ニーズ（本人・保護者）
        ttk.Label(needs_frame, text="ニーズ（本人）:").grid(row=3, column=0, sticky="nw", pady=5)
        self.child_needs = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：宿題など学習を進めないといけない気持ちはある",
            options=[
                "宿題など学習を進めないといけない気持ちはある",
                "勉強ができるようになりたいが、どこから始めればいいかわからない",
                "友達と同じように授業についていけるようになりたい",
                "学習に対する自信を取り戻したい",
                "特に学習に関するニーズはない"
            ]
        )
        self.child_needs.grid(row=3, column=1, columnspan=2, sticky="w", padx=5)
        
        ttk.Label(needs_frame, text="ニーズ（保護者）:").grid(row=4, column=0, sticky="nw", pady=5)
        self.guardian_needs = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：学習に取り組んでほしい",
            options=[
                "学習に取り組んでほしい",
                "本人に合った学習方法を見つけてほしい",
                "学習習慣を身につけてほしい",
                "本人のペースで学習を進めてほしい",
                "特に学習に関する要望はない"
            ]
        )
        self.guardian_needs.grid(row=4, column=1, columnspan=2, sticky="w", padx=5)
        
        # 目標
        ttk.Label(needs_frame, text="目標:").grid(row=5, column=0, sticky="nw", pady=5)
        self.short_term_goal = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：本人の自己肯定感と学習意欲を高める。学習の遅れを取り戻す。",
            options=[
                "本人の自己肯定感と学習意欲を高める。学習の遅れを取り戻す。",
                "学習習慣を身につけ、基礎学力を向上させる。",
                "本人に合った学習方法を見つけ、自信を回復させる。",
                "学習環境を整え、継続的な学習を支援する。",
                "学習に対する前向きな姿勢を育成する。"
            ]
        )
        self.short_term_goal.grid(row=5, column=1, columnspan=2, sticky="w", padx=5)
        
        # 具体的な方法
        ttk.Label(needs_frame, text="具体的な方法:").grid(row=6, column=0, sticky="nw", pady=5)
        self.short_term_method = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：本人の特性について理解を深める、本人に合った学習方法の提案、学び直しのための計画、学習の見守り",
            options=[
                "本人の特性について理解を深める、本人に合った学習方法の提案、学び直しのための計画、学習の見守り",
                "学習環境の整備、家族との連携、段階的な学習計画の策定、継続的なサポート",
                "本人の興味関心を活用した学習アプローチ、成功体験の積み重ね、自己肯定感の向上",
                "学習支援ツールの活用、個別指導の実施、進捗の定期的な確認と調整",
                "家族との協力体制の構築、学校との連携、本人のペースに合わせた支援"
            ]
        )
        self.short_term_method.grid(row=6, column=1, columnspan=2, sticky="w", padx=5)
        
        # 長期目標セクション
        ttk.Label(needs_frame, text="<本事業における達成目標>", font=("游ゴシック", 10, "bold")).grid(row=7, column=0, columnspan=3, sticky="w", pady=(20, 10))
        
        # 課題
        ttk.Label(needs_frame, text="課題:").grid(row=8, column=0, sticky="nw", pady=5)
        self.long_term_issue = PlaceholderCombobox(
            needs_frame, 
            width=27,
            placeholder="例：進路について情報不足",
            options=[
                "進路について情報不足",
                "将来の目標が明確でない",
                "就職・進学の準備不足",
                "自立に向けたスキル不足",
                "社会性の向上が必要"
            ]
        )
        self.long_term_issue.grid(row=8, column=1, sticky="w", padx=5)
        
        # 現状
        ttk.Label(needs_frame, text="現状:").grid(row=9, column=0, sticky="nw", pady=5)
        self.long_term_current = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：本人はできれば進学はしたいが、諦めてしまっている状態",
            options=[
                "本人はできれば進学はしたいが、諦めてしまっている状態",
                "将来の目標が明確でなく、進路選択に迷っている状態",
                "就職や進学に向けた準備ができておらず、不安を感じている",
                "自立に向けたスキルが不足しており、将来に不安がある",
                "社会性やコミュニケーション能力の向上が必要な状態"
            ]
        )
        self.long_term_current.grid(row=9, column=1, columnspan=2, sticky="w", padx=5)
        
        # ニーズ（本人・保護者）
        ttk.Label(needs_frame, text="ニーズ（本人）:").grid(row=10, column=0, sticky="nw", pady=5)
        self.child_needs_long = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：できれば進学したい",
            options=[
                "できれば進学したい",
                "将来の目標を明確にしたい",
                "就職に向けた準備をしたい",
                "自立に向けたスキルを身につけたい",
                "社会性を向上させたい"
            ]
        )
        self.child_needs_long.grid(row=10, column=1, columnspan=2, sticky="w", padx=5)
        
        ttk.Label(needs_frame, text="ニーズ（保護者）:").grid(row=11, column=0, sticky="nw", pady=5)
        self.guardian_needs_long = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：本人に合った進路選択をしてほしい",
            options=[
                "本人に合った進路選択をしてほしい",
                "将来の目標を一緒に考えてほしい",
                "就職に向けた準備をサポートしてほしい",
                "自立に向けたスキルを身につけさせてほしい",
                "社会性を向上させてほしい"
            ]
        )
        self.guardian_needs_long.grid(row=11, column=1, columnspan=2, sticky="w", padx=5)
        
        # 目標
        ttk.Label(needs_frame, text="目標:").grid(row=12, column=0, sticky="nw", pady=5)
        self.long_term_goal = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：本人に合った進路選択をする",
            options=[
                "本人に合った進路選択をする",
                "将来の目標を明確にし、具体的な計画を立てる",
                "就職に向けた準備を完了し、自立を目指す",
                "自立に向けたスキルを身につけ、社会参加を実現する",
                "社会性を向上させ、良好な人間関係を築く"
            ]
        )
        self.long_term_goal.grid(row=12, column=1, columnspan=2, sticky="w", padx=5)
        
        # 具体的な方法
        ttk.Label(needs_frame, text="具体的な方法:").grid(row=13, column=0, sticky="nw", pady=5)
        self.long_term_method = PlaceholderCombobox(
            needs_frame, 
            width=57,
            placeholder="例：本人の進学に対するニーズ聞き取り、サポートが手厚い学校などの情報提供、受験対策",
            options=[
                "本人の進学に対するニーズ聞き取り、サポートが手厚い学校などの情報提供、受験対策",
                "将来の目標設定支援、職業体験の機会提供、進路相談の実施、具体的な計画策定",
                "就職活動支援、面接練習、履歴書作成支援、職業訓練の情報提供、就職先の開拓",
                "生活スキル訓練、コミュニケーション能力向上、社会参加活動、自立準備プログラム",
                "社会性向上プログラム、人間関係構築支援、コミュニティ活動参加、継続的なフォローアップ"
            ]
        )
        self.long_term_method.grid(row=13, column=1, columnspan=2, sticky="w", padx=5)
        
        # マウスホイールでテキストエリア内スクロール（ScrolledTextのみ）
        # PlaceholderEntryに変更された項目は除外
        
        # === セクション9：支援への希望 ===
        support_wishes_frame = ttk.LabelFrame(scrollable_frame, text="🎯 支援への希望", padding=15)
        support_wishes_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(support_wishes_frame, text="希望の曜日:").grid(row=0, column=0, sticky="w", pady=5)
        
        # 曜日選択用のフレーム
        day_selection_frame = tk.Frame(support_wishes_frame)
        day_selection_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        # 平日の曜日チェックボックス
        self.preferred_days = {}
        weekdays = ["月", "火", "水", "木", "金"]
        for i, day in enumerate(weekdays):
            var = tk.BooleanVar()
            ttk.Checkbutton(day_selection_frame, text=day, variable=var).grid(row=0, column=i, sticky="w", padx=2)
            self.preferred_days[day] = var
        
        ttk.Label(support_wishes_frame, text="希望の時間帯:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.preferred_time_entry = PlaceholderCombobox(
            support_wishes_frame, 
            width=17,
            placeholder="例：14:00-16:00",
            options=[
                "14:00-16:00",
                "10:00-12:00",
                "13:00-15:00",
                "15:00-17:00",
                "16:00-18:00"
            ]
        )
        self.preferred_time_entry.grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(support_wishes_frame, text="希望の場所:").grid(row=1, column=0, sticky="w", pady=5)
        self.preferred_location_entry = PlaceholderCombobox(
            support_wishes_frame, 
            width=27,
            placeholder="例：自宅、区役所",
            options=[
                "自宅、区役所",
                "自宅のみ",
                "区役所のみ",
                "学校、自宅",
                "その他の場所"
            ]
        )
        self.preferred_location_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(support_wishes_frame, text="希望の支援員:").grid(row=1, column=2, sticky="w", padx=(20, 5))
        
        # 支援員選択用のフレーム
        supporter_frame = tk.Frame(support_wishes_frame)
        supporter_frame.grid(row=1, column=3, sticky="w", padx=5)
        
        self.preferred_supporter_entry = PlaceholderCombobox(
            supporter_frame, 
            width=15,
            placeholder="例：同性、年齢近い",
            options=[
                "同性、年齢近い",
                "同性、年上",
                "異性、年齢近い",
                "年齢は問わない",
                "特に希望なし"
            ]
        )
        self.preferred_supporter_entry.pack(side="left")
        
        # 支援員検索ボタン
        search_staff_btn = tk.Button(
            supporter_frame,
            text="🔍 検索",
            font=("游ゴシック", 8),
            bg="#3498db",
            fg="white",
            command=self.search_staff,
            padx=8,
            pady=2
        )
        search_staff_btn.pack(side="left", padx=(5, 0))
        
        ttk.Label(support_wishes_frame, text="解決したいこと:").grid(row=2, column=0, sticky="nw", pady=5)
        self.support_goals_text = PlaceholderTextArea(
            support_wishes_frame,
            width=60,
            height=3,
            wrap=tk.WORD,
            placeholder="例：生活リズムを整えたい、友達を作りたい",
            options=[
                "生活リズムを整えたい、友達を作りたい",
                "学校に行けるようになりたい、勉強を頑張りたい",
                "自信を持ちたい、自分の気持ちを伝えられるようになりたい",
                "規則正しい生活を送りたい、家族関係を改善したい",
                "将来の目標を見つけたい、自分らしく生きたい"
            ]
        )
        self.support_goals_text.grid(row=2, column=1, columnspan=3, sticky="w", padx=5)
        
        # マウスホイールでテキストエリア内スクロール
        def _on_support_goals_mousewheel(event):
            self.support_goals_text.text_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        self.support_goals_text.inner_text.bind("<MouseWheel>", _on_support_goals_mousewheel)
        
        # === セクション10：当日の様子（自由記述） ===
        memo_frame = ttk.LabelFrame(scrollable_frame, text="📝 当日の様子・その他メモ", padding=15)
        memo_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        hint_label = tk.Label(
            memo_frame,
            text="💡 服装、表情、会話の流れ、気になった点など自由に記録",
            fg="gray"
        )
        hint_label.pack(anchor="w", pady=(0, 5))
        
        self.memo_text = scrolledtext.ScrolledText(
            memo_frame,
            wrap=tk.WORD,
            width=80,
            height=8,
            font=("游ゴシック", 11)
        )
        self.memo_text.pack(fill="both", expand=True)
        
        # マウスホイールでテキストエリア内スクロール
        def _on_memo_mousewheel(event):
            self.memo_text.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        self.memo_text.bind("<MouseWheel>", _on_memo_mousewheel)
        
        # === ボタンエリア ===
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        preview_btn = tk.Button(
            button_frame,
            text="👀 プレビュー",
            font=("游ゴシック", 11),
            command=self.show_preview,
            padx=15,
            pady=8
        )
        preview_btn.pack(side="left", padx=5)
        
        complete_btn = tk.Button(
            button_frame,
            text="✅ 完成・保存",
            font=("游ゴシック", 12, "bold"),
            bg="#7ED321",
            fg="white",
            command=self.on_complete_clicked,
            padx=20,
            pady=10
        )
        complete_btn.pack(side="right")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # すべてのウィジェットにマウスホイールバインド
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # すべてのフレームにマウスホイールイベントを伝播
        frames = [basic_frame, attendance_frame, life_frame, study_frame, social_frame, 
                 dev_frame, family_frame, needs_frame, support_wishes_frame, memo_frame, button_frame]
        
        for frame in frames:
            frame.bind("<MouseWheel>", _on_mousewheel)
            # フレーム内のすべての子ウィジェットにもバインド
            self._bind_mousewheel_to_children(frame, _on_mousewheel)
    
    def _bind_mousewheel_to_children(self, widget, callback):
        """ウィジェットとその子ウィジェットすべてにマウスホイールイベントをバインド"""
        try:
            widget.bind("<MouseWheel>", callback)
            # 子ウィジェットを再帰的に処理
            for child in widget.winfo_children():
                self._bind_mousewheel_to_children(child, callback)
        except:
            # バインドできないウィジェット（例：Canvas内のウィンドウ）はスキップ
            pass

    def toggle_medical_fields(self):
        """通院情報の表示/非表示切り替え"""
        if self.medical_check_var.get():
            self.medical_detail_frame.grid()
        else:
            self.medical_detail_frame.grid_remove()
    
    def show_preview(self):
        """プレビュー表示"""
        if not self.validate_input():
            return
        
        assessment_data = self.generate_assessment_data()
        messagebox.showinfo(
            "プレビュー",
            f"課題チェック数: {self.count_checked_issues()}件\n"
            f"本人ニーズ: {self.child_needs.get('1.0', tk.END).strip()[:30]}...\n"
            f"保護者ニーズ: {self.guardian_needs.get('1.0', tk.END).strip()[:30]}...\n\n"
            "「完成・保存」ボタンでアセスメントシートと報告書を作成します"
        )
    
    def count_checked_issues(self):
        """チェックされた課題の数をカウント"""
        count = 0
        if self.truancy_check.get():
            count += 1
        for var in self.rhythm_checks.values():
            if var.get():
                count += 1
        for var in self.habit_checks.values():
            if var.get():
                count += 1
        for var in self.study_checks.values():
            if var.get():
                count += 1
        for var in self.social_checks.values():
            if var.get():
                count += 1
        if self.dev_check_var.get():
            count += 1
        for var in self.family_checks.values():
            if var.get():
                count += 1
        return count
    
    def on_complete_clicked(self):
        """完成ボタンクリック時"""
        if not self.validate_input():
            return
        
        interview_data = self.get_interview_data()
        assessment_data = self.generate_assessment_data()
        
        try:
            # Excelファイル生成
            excel_path = self.generate_excel_file(interview_data, assessment_data)
            
            # 報告書内容をクリップボードにコピー
            self.copy_report_to_clipboard(interview_data, assessment_data)
            
            # 成功メッセージ
            if excel_path:
                messagebox.showinfo(
                    "完成！",
                    "✅ アセスメントシートと報告書が完成しました！\n\n"
                    f"📁 Excelファイル: {excel_path}\n"
                    "📋 報告書内容: クリップボードにコピーされました\n\n"
                    "報告書に貼り付けてご利用ください。"
                )
            else:
                messagebox.showinfo(
                    "完成！",
                    "✅ 報告書が完成しました！\n\n"
                    "📋 報告書内容: クリップボードにコピーされました\n\n"
                    "報告書に貼り付けてご利用ください。"
                )
            
        except Exception as e:
            messagebox.showerror(
                "エラー",
                f"ファイル生成中にエラーが発生しました:\n\n{str(e)}\n\n"
                "詳細はコンソールを確認してください。"
            )
            print(f"❌ エラー詳細: {str(e)}")
        
        # 従来のコールバックも実行
        self.on_complete_callback(interview_data, assessment_data)
    
    def generate_excel_file(self, interview_data, assessment_data):
        """Excelファイルを生成（Dropbox対応版）"""
        try:
            from src.excel.assessment_writer import AssessmentWriter
            import config
            
            # テンプレートファイルのパスを取得
            template_path = config.TEMPLATE_DIR / "アセスメントシート原本.xlsx"
            
            if not template_path.exists():
                messagebox.showerror("エラー", f"テンプレートファイルが見つかりません:\n{template_path}")
                return None
            
            # ファイル名を生成
            child_name = interview_data.get('児童氏名', '未記録')
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"アセスメントシート_{child_name}_{date_str}.xlsx"
            
            # 保存先を選択（ダイアログを表示）
            # 初期フォルダを決定（Dropbox優先、なければダウンロードフォルダ）
            if config.USE_DROPBOX and config.check_dropbox_available():
                dropbox_path = config.get_dropbox_path()
                initial_dir = str(dropbox_path)
                dialog_title = "アセスメントシートの保存場所を選択してください（Dropbox）"
            else:
                # ローカル保存の場合はダウンロードフォルダを初期フォルダに
                downloads_dir = Path.home() / "Downloads"
                initial_dir = str(downloads_dir)
                dialog_title = "アセスメントシートの保存場所を選択してください"
            
            output_path = filedialog.asksaveasfilename(
                title=dialog_title,
                defaultextension=".xlsx",
                filetypes=[
                    ("Excelファイル", "*.xlsx"),
                    ("すべてのファイル", "*.*")
                ],
                initialfile=filename,
                initialdir=initial_dir
            )
            
            if not output_path:
                messagebox.showwarning("警告", "保存場所が選択されませんでした。")
                return None
            
            output_path = Path(output_path)
            
            # 保存先の種類を判定
            if config.USE_DROPBOX and config.check_dropbox_available():
                dropbox_path = config.get_dropbox_path()
                if dropbox_path and str(output_path).startswith(str(dropbox_path)):
                    save_location = "Dropbox"
                    location_icon = "☁️"
                else:
                    save_location = "ローカル"
                    location_icon = "💾"
            else:
                save_location = "ローカル"
                location_icon = "💾"
            
            # Excelファイル生成
            writer = AssessmentWriter(str(template_path))
            writer.create_assessment_file(interview_data, assessment_data, output_path)
            
            # 成功メッセージ
            message = (
                f"アセスメントシートを作成しました！\n\n"
                f"{location_icon} 保存先: {save_location}\n"
                f"📁 {output_path}\n\n"
            )
            
            # Dropboxの場合は追加情報
            if save_location == "Dropbox":
                message += (
                    "✅ Dropboxで自動的に同期されます\n"
                    "👥 チームメンバーも閲覧可能です"
                )
            
            messagebox.showinfo("出力完了", message)
            
            print(f"✅ Excelファイル生成完了: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Excelファイル生成エラー: {str(e)}")
            messagebox.showerror("エラー", f"Excelファイルの生成に失敗しました:\n{str(e)}")
            raise
    
    def copy_report_to_clipboard(self, interview_data, assessment_data):
        """報告書内容をクリップボードにコピー"""
        try:
            report_text = self.generate_report_text(interview_data, assessment_data)
            pyperclip.copy(report_text)
            print("✅ 報告書内容をクリップボードにコピーしました")
            
        except Exception as e:
            print(f"❌ クリップボードコピーエラー: {str(e)}")
            raise
    
    def generate_report_text(self, interview_data, assessment_data):
        """報告書テキストを生成"""
        print("🔧 デバッグ: generate_report_text が呼び出されました")
        
        # 短期目標の情報を取得
        short_term_plan = assessment_data.get('short_term_plan', {})
        
        # 長期目標の情報を取得
        long_term_plan = assessment_data.get('long_term_plan', {})
        
        # 報告書テキストを構築（本人情報を最初に配置）
        report_text = "【面談記録】\n\n"
        
        # 面談内容
        report_text += "【面談内容】\n"
        report_text += f"{interview_data.get('メモ', '未記録')}\n\n"
        
        # 本人情報（最初に配置）
        report_text += "【本人情報】\n"
        report_text += f"・氏名：{interview_data.get('児童氏名', '未記録')}\n"
        report_text += f"・学校：{interview_data.get('学校名', '未記録')} {interview_data.get('学年', '未記録')}年生\n"
        report_text += f"・性別：{interview_data.get('性別', '未記録')}\n"
        report_text += f"・家族構成：{interview_data.get('家族構成', '未記録')}\n"
        report_text += f"・趣味・好きなこと：{interview_data.get('趣味・好きなこと', '未記録')}\n\n"
        
        # 近況
        report_text += "【近況】\n"
        report_text += "【登校状況】\n"
        report_text += f"{self.format_attendance_info(assessment_data)}\n\n"
        
        report_text += "【生活状況】\n"
        report_text += f"{self.format_life_info(assessment_data)}\n\n"
        
        report_text += "【学習状況】\n"
        report_text += f"{self.format_study_info(assessment_data)}\n\n"
        
        report_text += "【対人関係】\n"
        report_text += f"{self.format_social_info(assessment_data)}\n\n"
        
        report_text += "【発達・医療情報】\n"
        report_text += f"{self.format_medical_info(interview_data, assessment_data)}\n\n"
        
        report_text += "【家庭環境】\n"
        report_text += f"{self.format_family_info(assessment_data)}\n\n"
        
        # 短期目標
        report_text += "【短期目標】\n"
        report_text += f"・課題：{short_term_plan.get('課題', '未記録')}\n"
        report_text += f"・現状：{short_term_plan.get('現状', '未記録')}\n"
        report_text += f"・ニーズ（本人）：{short_term_plan.get('ニーズ_本人', '未記録')}\n"
        report_text += f"・ニーズ（保護者）：{short_term_plan.get('ニーズ_保護者', '未記録')}\n"
        report_text += f"・目標：{short_term_plan.get('目標', '未記録')}\n"
        report_text += f"・具体的な方法：{short_term_plan.get('具体的な方法', '未記録')}\n\n"
        
        # 本事業における達成目標
        report_text += "【本事業における達成目標】\n"
        report_text += f"・課題：{long_term_plan.get('課題', '未記録')}\n"
        report_text += f"・現状：{long_term_plan.get('現状', '未記録')}\n"
        report_text += f"・ニーズ（本人）：{long_term_plan.get('ニーズ_本人', '未記録')}\n"
        report_text += f"・ニーズ（保護者）：{long_term_plan.get('ニーズ_保護者', '未記録')}\n"
        report_text += f"・目標：{long_term_plan.get('目標', '未記録')}\n"
        report_text += f"・具体的な方法：{long_term_plan.get('具体的な方法', '未記録')}\n\n"
        
        # 支援への希望
        report_text += "【支援への希望】\n"
        report_text += f"・希望の曜日：{interview_data.get('支援への希望', {}).get('希望の曜日', '未記録')}\n"
        report_text += f"・希望の時間帯：{interview_data.get('支援への希望', {}).get('希望の時間帯', '未記録')}\n"
        report_text += f"・希望の場所：{interview_data.get('支援への希望', {}).get('希望の場所', '未記録')}\n"
        report_text += f"・希望の支援員：{interview_data.get('支援への希望', {}).get('希望の支援員', '未記録')}\n"
        report_text += f"・解決したいこと：{interview_data.get('支援への希望', {}).get('解決したいこと', '未記録')}\n\n"
        
        # 面談実施日
        report_text += "【面談実施日】\n"
        if isinstance(interview_data.get('面談実施日'), datetime):
            report_text += f"{interview_data.get('面談実施日').strftime('%Y年%m月%d日')}\n"
        else:
            report_text += "未記録\n"
        
        return report_text
    
    def format_attendance_info(self, assessment_data):
        """登校状況の情報を整形"""
        attendance = assessment_data.get('attendance', {})
        if attendance.get('不登校'):
            return f"不登校（{attendance.get('不登校期間', '期間不明')}）"
        else:
            return "登校している"
    
    def format_life_info(self, assessment_data):
        """生活状況の情報を整形"""
        life_info = assessment_data.get('life_situation', {})
        info_parts = []
        
        if life_info.get('生活リズム_課題'):
            info_parts.append(f"生活リズム：{', '.join(life_info.get('生活リズム_課題', []))}")
        if life_info.get('生活習慣_課題'):
            info_parts.append(f"生活習慣：{', '.join(life_info.get('生活習慣_課題', []))}")
        if life_info.get('外出状況'):
            info_parts.append(f"外出状況：{life_info.get('外出状況', '未記録')}")
            
        return '\n'.join(info_parts) if info_parts else "特に問題なし"
    
    def format_study_info(self, assessment_data):
        """学習状況の情報を整形"""
        study_info = assessment_data.get('study_situation', {})
        if study_info.get('学習_課題'):
            return f"学習課題：{', '.join(study_info.get('学習_課題', []))}"
        else:
            return "特に問題なし"
    
    def format_social_info(self, assessment_data):
        """対人関係の情報を整形"""
        social_info = assessment_data.get('social_situation', {})
        if social_info.get('対人関係_課題'):
            return f"対人関係課題：{', '.join(social_info.get('対人関係_課題', []))}"
        else:
            return "特に問題なし"
    
    def format_medical_info(self, interview_data, assessment_data):
        """医療情報を整形"""
        medical_info = []
        
        # 通院状況
        medical_status = interview_data.get('通院状況', {})
        if medical_status.get('通院あり'):
            medical_info.append(f"通院あり：{medical_status.get('病院名', '未記録')}")
            if medical_status.get('診断名'):
                medical_info.append(f"診断：{medical_status.get('診断名', '未記録')}")
            if medical_status.get('投薬'):
                medical_info.append(f"投薬：{medical_status.get('投薬', '未記録')}")
            if medical_status.get('手帳'):
                medical_info.append(f"手帳：{medical_status.get('手帳', '未記録')}")
        else:
            medical_info.append("通院なし")
        
        # 発達特性
        dev_info = assessment_data.get('development', {})
        if dev_info.get('発達特性あり'):
            medical_info.append(f"発達特性：{dev_info.get('発達特性_詳細', '未記録')}")
        
        return '\n'.join(medical_info) if medical_info else "特に問題なし"
    
    def format_family_info(self, assessment_data):
        """家庭環境の情報を整形"""
        family_info = assessment_data.get('family_environment', {})
        if family_info.get('家庭環境_課題'):
            return f"家庭環境課題：{', '.join(family_info.get('家庭環境_課題', []))}"
        else:
            return "特に問題なし"
    
    def validate_input(self):
        """入力チェック"""
        errors = []
        
        if not self.child_name_entry.get().strip():
            errors.append("・児童氏名を入力してください")
        
        if not self.school_entry.get().strip():
            errors.append("・学校名を入力してください")
        
        if errors:
            messagebox.showerror(
                "入力エラー",
                "以下の項目を入力してください:\n\n" + "\n".join(errors)
            )
            return False
        
        return True
    
    def get_interview_data(self):
        """入力データを収集"""
        data = {
            '児童氏名': self.child_name_entry.get().strip(),
            '保護者氏名': self.guardian_name_entry.get().strip(),
            '性別': self.gender_var.get(),
            '学校名': self.school_entry.get().strip(),
            '学年': int(self.grade_spinbox.get()),
            '家族構成': self.family_structure_entry.get().strip(),
            '趣味・好きなこと': self.hobbies_entry.get().strip(),
            'ひとり親世帯': self.single_parent_var.get(),
            '担当支援員': self.supporter_entry.get().strip(),
            '面談実施日': datetime.strptime(
                self.interview_date_entry.get(),
                '%Y/%m/%d'
            ),
            'メモ': self.memo_text.get("1.0", tk.END).strip(),
            '面談時間': '未記録',
            '面談場所': '未記録',
            '通院状況': {},
            '支援への希望': {
                '希望の曜日': self.get_selected_days(),
                '希望の時間帯': self.preferred_time_entry.get().strip(),
                '希望の場所': self.preferred_location_entry.get().strip(),
                '希望の支援員': self.preferred_supporter_entry.get().strip(),
                '解決したいこと': self.support_goals_text.get()
            }
        }
        
        if self.medical_check_var.get():
            data['通院状況'] = {
                '通院あり': True,
                '病院名': self.hospital_entry.get().strip(),
                '診断名': self.diagnosis_entry.get().strip(),
                '頻度': self.frequency_entry.get().strip(),
                '投薬': self.medication_entry.get().strip(),
                '手帳': self.handbook_entry.get().strip()
            }
        else:
            data['通院状況'] = {'通院あり': False}
        
        return data
    
    def get_selected_days(self):
        """選択された曜日を取得"""
        selected_days = []
        for day, var in self.preferred_days.items():
            if var.get():
                selected_days.append(day)
        return '・'.join(selected_days) if selected_days else ''
    
    def generate_assessment_data(self):
        """アセスメントデータを生成"""
        issues = {}
        
        # 不登校
        issues["不登校"] = {
            "該当": self.truancy_check.get(),
            "詳細": f"{self.attendance_var.get()}。{self.truancy_detail.get()}"
        }
        
        # 引きこもり
        outing = self.outing_var.get()
        issues["引きこもり"] = {
            "該当": outing == "ほぼ外出しない",
            "詳細": outing
        }
        
        # 生活リズム
        rhythm_items = [k for k, v in self.rhythm_checks.items() if v.get()]
        rhythm_detail_text = self.rhythm_detail.get().strip()
        issues["生活リズム"] = {
            "該当": len(rhythm_items) > 0 and "特に問題なし" not in rhythm_items,
            "詳細": f"、".join(rhythm_items) + (f"({rhythm_detail_text})" if rhythm_detail_text else "") if rhythm_items else "特に問題なし"
        }
        
        # 生活習慣
        habit_items = [k for k, v in self.habit_checks.items() if v.get()]
        habit_detail_text = self.habit_detail.get().strip()
        issues["生活習慣"] = {
            "該当": len(habit_items) > 0 and "特に問題なし" not in habit_items,
            "詳細": f"、".join(habit_items) + (f"({habit_detail_text})" if habit_detail_text else "") if habit_items else "特に問題なし"
        }
        
        # 学習
        study_items = [k for k, v in self.study_checks.items() if v.get()]
        study_detail_text = self.study_detail.get().strip()
        issues["学習の遅れ・低学力"] = {
            "該当": any(item in study_items for item in ["学習の遅れ", "低学力"]),
            "詳細": f"、".join(study_items) + (f"({study_detail_text})" if study_detail_text else "") if study_items else "特に問題なし"
        }
        
        issues["学習習慣・環境"] = {
            "該当": any(item in study_items for item in ["学習習慣なし", "学習環境なし"]),
            "詳細": f"、".join(study_items) + (f"({study_detail_text})" if study_detail_text else "") if study_items else "特に問題なし"
        }
        
        # 発達特性
        issues["発達特性or発達課題"] = {
            "該当": self.dev_check_var.get(),
            "詳細": self.dev_detail.get() if self.dev_check_var.get() else "該当なし"
        }
        
        # 対人関係
        social_items = [k for k, v in self.social_checks.items() if v.get()]
        social_detail_text = self.social_detail.get().strip()
        issues["対人緊張の高さ"] = {
            "該当": "対人緊張が高い" in social_items or "友達との関わりに不安" in social_items,
            "詳細": f"、".join(social_items) + (f"({social_detail_text})" if social_detail_text else "") if social_items else "特に問題なし"
        }
        
        issues["コミュニケーションに苦手意識"] = {
            "該当": "コミュニケーション苦手" in social_items,
            "詳細": f"、".join(social_items) + (f"({social_detail_text})" if social_detail_text else "") if social_items else "特に問題なし"
        }
        
        # 家庭環境
        family_items = [k for k, v in self.family_checks.items() if v.get()]
        family_detail_text = self.family_detail.get().strip()
        issues["家庭環境"] = {
            "該当": len(family_items) > 0 and "特に問題なし" not in family_items,
            "詳細": f"、".join(family_items) + (f"({family_detail_text})" if family_detail_text else "") if family_items else "特に問題なし"
        }
        
        issues["虐待"] = {
            "該当": "虐待" in family_items,
            "詳細": f"虐待({family_detail_text})" if "虐待" in family_items and family_detail_text else "該当なし"
        }
        issues["他の世帯員の問題"] = {
            "該当": "他の世帯員の問題" in family_items,
            "詳細": f"他の世帯員の問題({family_detail_text})" if "他の世帯員の問題" in family_items and family_detail_text else "該当なし"
        }
        issues["その他"] = {
            "該当": "その他" in family_items,
            "詳細": f"その他({family_detail_text})" if "その他" in family_items and family_detail_text else ""
        }
        
        # 短期・長期目標の構造化
        short_term_plan = {
            "課題": self.short_term_issue.get().strip(),
            "現状": self.short_term_current.get().strip(),
            "ニーズ_本人": self.child_needs.get().strip(),
            "ニーズ_保護者": self.guardian_needs.get().strip(),
            "目標": self.short_term_goal.get().strip(),
            "方法": self.short_term_method.get().strip()
        }
        
        long_term_plan = {
            "課題": self.long_term_issue.get().strip(),
            "現状": self.long_term_current.get().strip(),
            "ニーズ_本人": self.child_needs_long.get().strip(),
            "ニーズ_保護者": self.guardian_needs_long.get().strip(),
            "目標": self.long_term_goal.get().strip(),
            "方法": self.long_term_method.get().strip()
        }
        
        # 希望する進路（現在は未実装のため空のデータを返す）
        future_path = {
            "type": "",
            "detail": ""
        }
        
        return {
            "issues": issues,
            "short_term_plan": short_term_plan,
            "long_term_plan": long_term_plan,
            "future_path": future_path,
            "missing_info": []
        }
    
    def search_staff(self):
        """支援員検索ダイアログを開く"""
        try:
            from src.ui.staff_selector import StaffSelectorDialog
            
            # 現在の支援希望データを取得
            support_wishes = self.get_support_wishes()
            
            # 支援員選択ダイアログを開く
            dialog = StaffSelectorDialog(self, support_wishes)
            dialog.wait_window()
            
            # 選択された支援員がいる場合、入力フィールドに反映
            if hasattr(dialog, 'selected_staff') and dialog.selected_staff:
                staff = dialog.selected_staff
                staff_info = f"{staff['name']} ({staff['age']}歳, {staff['gender']}, {staff['region']})"
                self.preferred_supporter_entry.set(staff_info)
                
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("エラー", f"支援員検索中にエラーが発生しました:\n{str(e)}")
    
    def get_support_wishes(self):
        """現在の支援希望データを取得"""
        # 選択された曜日を取得
        selected_days = [day for day, var in self.preferred_days.items() if var.get()]
        
        return {
            'preferred_region': '',  # 地域は現在未実装
            'age_range': '',  # 年齢範囲は現在未実装
            'gender_preference': '',  # 性別希望は現在未実装
            'preferred_day': ','.join(selected_days),
            'preferred_time': self.preferred_time_entry.get().strip(),
            'preferred_location': self.preferred_location_entry.get().strip(),
            'interests': self.support_goals_text.get()
        }
