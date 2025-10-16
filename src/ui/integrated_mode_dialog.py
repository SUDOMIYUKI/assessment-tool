import tkinter as tk
from tkinter import ttk, messagebox
from src.database.templates import TemplateManager
from src.database.history import HistoryManager

class IntegratedModeDialog(tk.Toplevel):
    def __init__(self, parent, interview_data):
        super().__init__(parent)
        
        self.interview_data = interview_data
        self.template_manager = TemplateManager()
        self.history_manager = HistoryManager()
        
        self.title("データ活用モード - テンプレート・過去データ選択")
        self.geometry("1200x900")
        self.minsize(1100, 800)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # 中央に配置
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        # ヘッダー
        header_frame = tk.Frame(self, bg="#27AE60", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🔍 データ活用モード - テンプレート・過去データから選択",
            font=("游ゴシック", 14, "bold"),
            bg="#27AE60",
            fg="white"
        )
        title.pack(pady=(20, 5))
        
        subtitle = tk.Label(
            header_frame,
            text="📝テンプレートと📊過去データから最適な選択肢を選んでください",
            font=("游ゴシック", 10),
            bg="#27AE60",
            fg="white"
        )
        subtitle.pack(pady=(0, 20))
        
        # メインコンテナ（スクロール可能）
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # レイアウト
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # ウィンドウとキャンバスにバインド
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.bind("<MouseWheel>", _on_mousewheel)
        
        # ウィンドウが閉じられたときにバインドを解除
        def on_closing():
            try:
                canvas.unbind("<MouseWheel>")
                self.unbind("<MouseWheel>")
            except:
                pass
            self.destroy()
        
        self.protocol("WM_DELETE_WINDOW", on_closing)
        
        main_container = scrollable_frame
        
        # タブノートブック
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # 各タブを作成
        self.create_issues_tab()
        self.create_needs_tab()
        self.create_support_tab()
        self.create_path_tab()
        
        # ボタンエリア
        button_frame = tk.Frame(main_container, bg="#ECF0F1", relief="raised", bd=1)
        button_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # 説明文
        info_label = tk.Label(
            button_frame,
            text="📋 各項目でテンプレートまたは過去データから選択してから「決定」ボタンを押してください",
            font=("游ゴシック", 9),
            bg="#ECF0F1",
            fg="#2C3E50"
        )
        info_label.pack(pady=(10, 5))
        
        # ボタン
        button_row = tk.Frame(button_frame, bg="#ECF0F1")
        button_row.pack(pady=(0, 10))
        
        cancel_btn = tk.Button(
            button_row,
            text="❌ キャンセル",
            font=("游ゴシック", 11, "bold"),
            bg="#E74C3C",
            fg="white",
            command=self.destroy,
            padx=15,
            pady=8
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        create_btn = tk.Button(
            button_row,
            text="✅ 決定 - アセスメントを作成",
            font=("游ゴシック", 11, "bold"),
            bg="#27AE60",
            fg="white",
            command=self.create_assessment,
            padx=15,
            pady=8
        )
        create_btn.pack(side="left")
        
        print("🔧 デバッグ: 統合モードダイアログを作成しました")
    
    def create_issues_tab(self):
        """課題タブを作成"""
        issues_tab = ttk.Frame(self.notebook)
        self.notebook.add(issues_tab, text="📋 課題")
        
        # 課題の種類
        issues = [
            "不登校", "生活リズム", "学習", "人間関係", "家族関係", 
            "健康・体調", "進路・将来", "その他"
        ]
        
        self.issue_entries = {}
        
        for issue in issues:
            self.create_issue_section(issues_tab, issue)
    
    def create_issue_section(self, parent, issue_name):
        """課題セクションを作成"""
        section_frame = ttk.LabelFrame(parent, text=f"📋 {issue_name}", padding=10)
        section_frame.pack(fill="x", padx=10, pady=5)
        
        # テンプレートと過去データを取得
        templates = self.template_manager.get_templates('課題', issue_name)
        history_data = self.get_history_data_for_issue(issue_name)
        
        # 選択肢を作成
        options = []
        
        # テンプレートから追加
        for template in templates:
            if len(template) > 1:
                options.append(f"📝 {template[1]}")
        
        # 過去データから追加
        for i, data in enumerate(history_data):
            options.append(f"📊 過去ケース{i+1}: {data[:50]}...")
        
        # デフォルトオプション
        if not options:
            options = [f"{issue_name}に関する内容を記入してください"]
        
        # コンボボックス
        combo = ttk.Combobox(section_frame, values=options, width=80)
        combo.pack(fill="x", pady=5)
        
        # カスタム入力
        custom_entry = tk.Entry(section_frame, width=80)
        custom_entry.pack(fill="x", pady=5)
        
        self.issue_entries[issue_name] = {
            'combo': combo,
            'custom': custom_entry
        }
    
    def get_history_data_for_issue(self, issue_name):
        """課題に関連する過去データを取得"""
        try:
            cases = self.history_manager.get_all_cases()
            relevant_data = []
            
            for case in cases:
                if len(case) > 5:  # memoが存在するかチェック
                    memo = case[5]  # memo列
                    if memo and issue_name.lower() in memo.lower():
                        relevant_data.append(memo)
            
            return relevant_data[:3]  # 最大3件まで
        except Exception as e:
            print(f"過去データ取得エラー: {e}")
            return []
    
    def create_needs_tab(self):
        """ニーズタブを作成"""
        needs_tab = ttk.Frame(self.notebook)
        self.notebook.add(needs_tab, text="🎯 ニーズ・目標")
        
        # ニーズ・目標の項目
        needs_items = [
            ("本人のニーズ", "ニーズ", "本人"),
            ("保護者のニーズ", "ニーズ", "保護者"),
            ("短期目標", "目標", "短期"),
            ("長期目標", "目標", "長期")
        ]
        
        self.needs_entries = {}
        
        for title, category, subcategory in needs_items:
            self.create_needs_section(needs_tab, title, category, subcategory)
    
    def create_needs_section(self, parent, title, category, subcategory):
        """ニーズセクションを作成"""
        section_frame = ttk.LabelFrame(parent, text=f"🎯 {title}", padding=10)
        section_frame.pack(fill="x", padx=10, pady=5)
        
        # テンプレートを取得
        templates = self.template_manager.get_templates(category, subcategory)
        
        # 選択肢を作成
        options = []
        
        # テンプレートから追加
        for template in templates:
            if len(template) > 1:
                options.append(f"📝 {template[1]}")
        
        # デフォルトオプション
        if not options:
            options = [f"{title}に関する内容を記入してください"]
        
        # コンボボックス
        combo = ttk.Combobox(section_frame, values=options, width=80)
        combo.pack(fill="x", pady=5)
        
        # カスタム入力
        custom_entry = tk.Entry(section_frame, width=80)
        custom_entry.pack(fill="x", pady=5)
        
        self.needs_entries[title] = {
            'combo': combo,
            'custom': custom_entry
        }
    
    def create_support_tab(self):
        """支援方法タブを作成"""
        support_tab = ttk.Frame(self.notebook)
        self.notebook.add(support_tab, text="🛠️ 支援方法")
        
        # 支援方法の項目
        support_items = [
            ("支援方法", "方法", "総合"),
            ("具体的支援", "方法", "具体的"),
            ("継続支援", "方法", "継続")
        ]
        
        self.support_entries = {}
        
        for title, category, subcategory in support_items:
            self.create_support_section(support_tab, title, category, subcategory)
    
    def create_support_section(self, parent, title, category, subcategory):
        """支援セクションを作成"""
        section_frame = ttk.LabelFrame(parent, text=f"🛠️ {title}", padding=10)
        section_frame.pack(fill="x", padx=10, pady=5)
        
        # テンプレートを取得
        templates = self.template_manager.get_templates(category, subcategory)
        
        # 選択肢を作成
        options = []
        
        # テンプレートから追加
        for template in templates:
            if len(template) > 1:
                options.append(f"📝 {template[1]}")
        
        # デフォルトオプション
        if not options:
            options = [f"{title}に関する内容を記入してください"]
        
        # コンボボックス
        combo = ttk.Combobox(section_frame, values=options, width=80)
        combo.pack(fill="x", pady=5)
        
        # カスタム入力
        custom_entry = tk.Entry(section_frame, width=80)
        custom_entry.pack(fill="x", pady=5)
        
        self.support_entries[title] = {
            'combo': combo,
            'custom': custom_entry
        }
    
    def create_path_tab(self):
        """進路タブを作成"""
        path_tab = ttk.Frame(self.notebook)
        self.notebook.add(path_tab, text="🎓 進路")
        
        frame = tk.Frame(path_tab, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="進路希望", font=("游ゴシック", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.path_type_var = tk.StringVar(value="進学")
        ttk.Radiobutton(frame, text="進学", variable=self.path_type_var, value="進学").pack(anchor="w")
        ttk.Radiobutton(frame, text="就職", variable=self.path_type_var, value="就職").pack(anchor="w")
        ttk.Radiobutton(frame, text="その他", variable=self.path_type_var, value="その他").pack(anchor="w", pady=(0, 10))
        
        ttk.Label(frame, text="具体的内容:", font=("游ゴシック", 11)).pack(anchor="w", pady=(10, 5))
        
        # 進路テンプレートを取得
        try:
            templates = self.template_manager.get_templates('進路')
            options = []
            
            # テンプレートから追加
            for template in templates:
                if len(template) > 1:
                    options.append(f"📝 {template[1]}")
            
            # 過去データから追加
            history_data = self.get_history_data_for_issue('進路')
            for i, data in enumerate(history_data):
                options.append(f"📊 過去ケース{i+1}: {data[:50]}...")
            
            # デフォルトオプション
            if not options:
                options = ["進路に関する内容を記入してください"]
            
            self.path_combo = ttk.Combobox(frame, values=options, width=80)
            self.path_combo.pack(anchor="w", pady=(0, 10))
            
        except Exception as e:
            print(f"進路テンプレート取得エラー: {e}")
            self.path_combo = ttk.Combobox(frame, values=["進路に関する内容を記入してください"], width=80)
            self.path_combo.pack(anchor="w", pady=(0, 10))
        
        # カスタム入力
        self.path_entry = tk.Entry(frame, width=80)
        self.path_entry.pack(anchor="w", pady=(0, 10))
    
    def create_assessment(self):
        """アセスメントを作成"""
        try:
            # 選択されたデータを収集
            assessment_data = self.collect_selected_data()
            
            # 親ウィンドウのコールバックを呼び出し
            if hasattr(self.master, 'on_integrated_mode_result'):
                self.master.on_integrated_mode_result(self.interview_data, assessment_data)
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("エラー", f"アセスメント作成中にエラーが発生しました：\n{str(e)}")
    
    def collect_selected_data(self):
        """選択されたデータを収集"""
        data = {
            'issues': {},
            'needs': {},
            'support': {},
            'path': {}
        }
        
        # 課題データを収集
        for issue_name, entries in self.issue_entries.items():
            combo_value = entries['combo'].get()
            custom_value = entries['custom'].get()
            
            if combo_value and not combo_value.startswith(issue_name):
                data['issues'][issue_name] = combo_value.replace("📝 ", "").replace("📊 ", "")
            elif custom_value:
                data['issues'][issue_name] = custom_value
        
        # ニーズデータを収集
        for needs_name, entries in self.needs_entries.items():
            combo_value = entries['combo'].get()
            custom_value = entries['custom'].get()
            
            if combo_value and not combo_value.startswith(needs_name):
                data['needs'][needs_name] = combo_value.replace("📝 ", "")
            elif custom_value:
                data['needs'][needs_name] = custom_value
        
        # 支援データを収集
        for support_name, entries in self.support_entries.items():
            combo_value = entries['combo'].get()
            custom_value = entries['custom'].get()
            
            if combo_value and not combo_value.startswith(support_name):
                data['support'][support_name] = combo_value.replace("📝 ", "")
            elif custom_value:
                data['support'][support_name] = custom_value
        
        # 進路データを収集
        path_combo_value = self.path_combo.get() if hasattr(self, 'path_combo') else ""
        path_custom_value = self.path_entry.get() if hasattr(self, 'path_entry') else ""
        
        if path_combo_value and not path_combo_value.startswith("進路"):
            data['path']['detail'] = path_combo_value.replace("📝 ", "").replace("📊 ", "")
        elif path_custom_value:
            data['path']['detail'] = path_custom_value
        
        data['path']['type'] = self.path_type_var.get() if hasattr(self, 'path_type_var') else "進学"
        
        return data
