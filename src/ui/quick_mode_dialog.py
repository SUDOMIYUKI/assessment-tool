import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from src.database.templates import TemplateManager

class QuickModeDialog(tk.Toplevel):
    def __init__(self, parent, interview_data):
        super().__init__(parent)
        
        self.interview_data = interview_data
        self.template_manager = TemplateManager()
        self.selected_templates = {
            'issues': {},
            'future_path': {'type': '不明', 'detail': ''},
            'short_term_plan': {
                '課題': '',
                '現状': '',
                'ニーズ_本人': '',
                'ニーズ_保護者': '',
                '目標': '',
                '方法': ''
            }
        }
        
        self.title("クイックモード - テンプレート選択")
        self.geometry("900x750")
        self.minsize(800, 650)
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
        header_frame = tk.Frame(self, bg="#7ED321", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="⚡ クイックモード - テンプレートから選択",
            font=("游ゴシック", 14, "bold"),
            bg="#7ED321",
            fg="white"
        )
        title.pack(pady=20)
        
        # メインコンテナ（ノートブック用）
        main_container = tk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ボタンエリア（メインコンテナ内に配置、目立つ色）
        button_frame = tk.Frame(main_container, bg="#d5dbdb", relief="raised", bd=5)
        button_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # ノートブック（タブ）
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill="both", expand=True)
        
        # タブ1: 課題選択
        issues_tab = ttk.Frame(notebook)
        notebook.add(issues_tab, text="📋 課題")
        self.create_issues_tab(issues_tab)
        
        # タブ2: ニーズ・目標
        plan_tab = ttk.Frame(notebook)
        notebook.add(plan_tab, text="🎯 ニーズ・目標")
        self.create_plan_tab(plan_tab)
        
        # タブ3: 支援方法
        method_tab = ttk.Frame(notebook)
        notebook.add(method_tab, text="🛠️ 支援方法")
        self.create_method_tab(method_tab)
        
        # タブ4: 進路
        path_tab = ttk.Frame(notebook)
        notebook.add(path_tab, text="🎓 進路")
        self.create_path_tab(path_tab)
        
        # ボタンエリア（シンプルなレイアウト）
        btn_inner_frame = tk.Frame(button_frame, bg="#d5dbdb")
        btn_inner_frame.pack(pady=10)
        
        # 説明ラベル
        info_label = tk.Label(
            btn_inner_frame,
            text="💡 項目を選択してから「決定」ボタンを押してください",
            font=("游ゴシック", 11, "bold"),
            bg="#d5dbdb",
            fg="#2c3e50"
        )
        info_label.pack(pady=(0, 10))
        
        # ボタン行
        button_row = tk.Frame(btn_inner_frame, bg="#d5dbdb")
        button_row.pack()
        
        cancel_btn = tk.Button(
            button_row,
            text="❌ キャンセル",
            font=("游ゴシック", 11),
            bg="#e74c3c",
            fg="white",
            command=self.destroy,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side="left", padx=(0, 15))
        
        create_btn = tk.Button(
            button_row,
            text="✅ 決定 - アセスメントを作成",
            font=("游ゴシック", 12, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.on_create,
            padx=30,
            pady=8,
            relief="raised",
            bd=3,
            cursor="hand2"
        )
        create_btn.pack(side="left")
        
        # テンプレート読み込みボタン
        import_btn = tk.Button(
            button_row,
            text="📚 過去ケースから読み込み",
            font=("游ゴシック", 10),
            bg="#3498db",
            fg="white",
            command=self.import_templates_from_history,
            padx=15,
            pady=8
        )
        import_btn.pack(side="left", padx=(15, 0))
        
        # ボタンにホバーエフェクトを追加
        def on_enter(e):
            create_btn['bg'] = '#2ecc71'
        def on_leave(e):
            create_btn['bg'] = '#27ae60'
        create_btn.bind("<Enter>", on_enter)
        create_btn.bind("<Leave>", on_leave)
        
        # デバッグ用：ボタンが作成されたことを確認
        print(f"🔧 デバッグ: 決定ボタンが作成されました - {create_btn['text']}")
        print(f"🔧 デバッグ: ボタンエリアのサイズ - {button_frame.winfo_reqwidth()}x{button_frame.winfo_reqheight()}")
        print(f"🔧 デバッグ: ボタンエリアの配置 - side='bottom'")
        print(f"🔧 デバッグ: メインコンテナ内に配置されています")
    
    def create_issues_tab(self, parent):
        """課題選択タブ"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイールスクロールを有効化
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # マウスがcanvasに入った時と出た時でイベントをバインド/アンバインド
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # 課題のチェックボックス
        self.issue_vars = {}
        self.issue_entries = {}
        
        issue_categories = [
            '不登校', '引きこもり', '生活リズム', '生活習慣',
            '学習の遅れ・低学力', '学習習慣・環境', '発達特性or発達課題',
            '対人緊張の高さ', 'コミュニケーションに苦手意識',
            '家庭環境', 'その他'
        ]
        
        for issue in issue_categories:
            issue_frame = ttk.LabelFrame(scrollable_frame, text=issue, padding=10)
            issue_frame.pack(fill="x", padx=10, pady=5)
            
            # チェックボックス
            var = tk.BooleanVar()
            self.issue_vars[issue] = var
            check = ttk.Checkbutton(
                issue_frame,
                text="該当する",
                variable=var,
                command=lambda i=issue: self.update_issue_entry(i)
            )
            check.pack(anchor="w")
            
            # テンプレート選択
            templates = self.template_manager.get_templates('課題', issue.split('・')[0])
            if templates:
                try:
                    combo_values = [t[1] for t in templates if len(t) > 1]
                    combo = ttk.Combobox(issue_frame, values=combo_values, width=70, state="readonly")
                    combo.pack(anchor="w", pady=(5, 0))
                    combo.bind('<<ComboboxSelected>>', lambda e, i=issue, c=combo: self.on_template_selected(i, c))
                    self.issue_entries[issue] = combo
                except (IndexError, TypeError):
                    combo = ttk.Combobox(issue_frame, values=[f"{issue}に関する内容を記入してください"], width=70, state="readonly")
                    combo.pack(anchor="w", pady=(5, 0))
                    combo.bind('<<ComboboxSelected>>', lambda e, i=issue, c=combo: self.on_template_selected(i, c))
                    self.issue_entries[issue] = combo
            else:
                combo = ttk.Combobox(issue_frame, values=[f"{issue}に関する内容を記入してください"], width=70, state="readonly")
                combo.pack(anchor="w", pady=(5, 0))
                combo.bind('<<ComboboxSelected>>', lambda e, i=issue, c=combo: self.on_template_selected(i, c))
                self.issue_entries[issue] = combo
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_plan_tab(self, parent):
        """ニーズ・目標タブ"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイールスクロールを有効化
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # マウスがcanvasに入った時と出た時でイベントをバインド/アンバインド
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        self.plan_combos = {}
        
        # 本人のニーズ
        self.create_template_section(scrollable_frame, "本人のニーズ", 'ニーズ', '本人', 'ニーズ_本人')
        
        # 保護者のニーズ
        self.create_template_section(scrollable_frame, "保護者のニーズ", 'ニーズ', '保護者', 'ニーズ_保護者')
        
        # 短期目標
        self.create_template_section(scrollable_frame, "短期目標", '目標', '短期', '目標')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_method_tab(self, parent):
        """支援方法タブ"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイールスクロールを有効化
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # マウスがcanvasに入った時と出た時でイベントをバインド/アンバインド
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # 支援方法
        self.create_template_section(scrollable_frame, "訪問支援", '方法', '訪問', '方法_訪問')
        self.create_template_section(scrollable_frame, "学習支援", '方法', '学習', '方法_学習')
        self.create_template_section(scrollable_frame, "交流支援", '方法', '交流', '方法_交流')
        self.create_template_section(scrollable_frame, "家族支援", '方法', '家族', '方法_家族')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_path_tab(self, parent):
        """進路タブ"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="進路希望", font=("游ゴシック", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.path_type_var = tk.StringVar(value="進学")
        ttk.Radiobutton(frame, text="進学", variable=self.path_type_var, value="進学").pack(anchor="w")
        ttk.Radiobutton(frame, text="就職", variable=self.path_type_var, value="就職").pack(anchor="w")
        ttk.Radiobutton(frame, text="その他", variable=self.path_type_var, value="その他").pack(anchor="w", pady=(0, 10))
        
        ttk.Label(frame, text="具体的内容:", font=("游ゴシック", 11)).pack(anchor="w", pady=(10, 5))
        
        # テンプレート取得を完全に安全に実行
        try:
            templates = self.template_manager.get_templates('進路')
            if templates and len(templates) > 0:
                try:
                    # get_templatesは (id, phrase) のタプルを返すので、t[1]がphrase
                    combo_values = []
                    for t in templates:
                        if isinstance(t, (tuple, list)) and len(t) > 1:
                            combo_values.append(t[1])
                    
                    if combo_values:
                        self.path_combo = ttk.Combobox(frame, values=combo_values, width=70)
                    else:
                        self.path_combo = ttk.Combobox(frame, values=["進路に関する内容を記入してください"], width=70)
                    self.path_combo.pack(anchor="w", pady=(0, 10))
                except (IndexError, TypeError) as e:
                    # テンプレートの形式が予期しない場合はデフォルト値を設定
                    print(f"テンプレート形式エラー: {e}")
                    self.path_combo = ttk.Combobox(frame, values=["進路に関する内容を記入してください"], width=70)
                    self.path_combo.pack(anchor="w", pady=(0, 10))
            else:
                # テンプレートがない場合はデフォルト値を設定
                self.path_combo = ttk.Combobox(frame, values=["進路に関する内容を記入してください"], width=70)
                self.path_combo.pack(anchor="w", pady=(0, 10))
        except Exception as e:
            # すべてのエラーをキャッチしてデフォルト値を設定
            print(f"進路テンプレート取得エラー: {e}")
            self.path_combo = ttk.Combobox(frame, values=["進路に関する内容を記入してください"], width=70)
            self.path_combo.pack(anchor="w", pady=(0, 10))
    
    def create_template_section(self, parent, title, category, subcategory, key):
        """テンプレート選択セクションを作成"""
        section_frame = ttk.LabelFrame(parent, text=title, padding=10)
        section_frame.pack(fill="x", padx=10, pady=5)
        
        templates = self.template_manager.get_templates(category, subcategory)
        if templates:
            try:
                combo_values = [t[1] for t in templates if len(t) > 1]
                combo = ttk.Combobox(section_frame, values=combo_values, width=70)
                combo.pack(anchor="w")
                self.plan_combos[key] = combo
            except (IndexError, TypeError):
                combo = ttk.Combobox(section_frame, values=[f"{category}に関する内容を記入してください"], width=70)
                combo.pack(anchor="w")
                self.plan_combos[key] = combo
        else:
            combo = ttk.Combobox(section_frame, values=[f"{category}に関する内容を記入してください"], width=70)
            combo.pack(anchor="w")
            self.plan_combos[key] = combo
    
    def update_issue_entry(self, issue):
        """課題チェックボックスの状態に応じてエントリを有効/無効化"""
        pass  # 現在は特に処理なし
    
    def on_template_selected(self, issue, combo):
        """テンプレートが選択された時"""
        # 自動的にチェックボックスをONにする
        if issue in self.issue_vars:
            self.issue_vars[issue].set(True)
    
    def on_create(self):
        """作成ボタンが押された時"""
        # 課題を収集
        for issue, var in self.issue_vars.items():
            if var.get():
                entry = self.issue_entries.get(issue)
                if entry:
                    if isinstance(entry, ttk.Combobox):
                        detail = entry.get()
                    else:
                        detail = entry.get()
                    
                    if detail:
                        self.selected_templates['issues'][issue] = detail
        
        # ニーズ・目標を収集
        for key, combo in self.plan_combos.items():
            value = combo.get()
            if value:
                if key.startswith('方法_'):
                    # 複数の支援方法を結合
                    if '方法' not in self.selected_templates['short_term_plan']:
                        self.selected_templates['short_term_plan']['方法'] = ''
                    if self.selected_templates['short_term_plan']['方法']:
                        self.selected_templates['short_term_plan']['方法'] += '\n'
                    self.selected_templates['short_term_plan']['方法'] += value
                else:
                    self.selected_templates['short_term_plan'][key] = value
        
        # 進路を収集
        self.selected_templates['future_path'] = {
            'type': self.path_type_var.get(),
            'detail': getattr(self, 'path_combo', None).get() if hasattr(self, 'path_combo') else getattr(self, 'path_entry', None).get() if hasattr(self, 'path_entry') else ''
        }
        
        self.destroy()
    
    def get_selected_templates(self):
        return self.selected_templates
    
    def import_templates_from_history(self):
        """過去ケースからテンプレートを読み込み"""
        try:
            # テンプレートをインポート
            count = self.template_manager.import_from_history()
            
            if count > 0:
                messagebox.showinfo(
                    "読み込み完了", 
                    f"過去のケースから {count} 個のテンプレートを読み込みました！\n\n各タブのテンプレート選択肢が更新されています。"
                )
                
                # 各タブのコンボボックスを更新
                self.refresh_template_combos()
            else:
                messagebox.showinfo(
                    "読み込み完了", 
                    "新しいテンプレートは見つかりませんでした。\n既存のテンプレートが使用されています。"
                )
                
        except Exception as e:
            messagebox.showerror(
                "エラー", 
                f"テンプレートの読み込み中にエラーが発生しました：\n{str(e)}"
            )
    
    def refresh_template_combos(self):
        """テンプレートコンボボックスを更新"""
        try:
            # 課題タブのコンボボックスを更新
            for issue, combo in self.issue_entries.items():
                if isinstance(combo, ttk.Combobox):
                    templates = self.template_manager.get_templates('課題', issue.split('・')[0])
                    if templates:
                        combo_values = [t[1] for t in templates]
                        combo['values'] = combo_values
            
            # ニーズ・目標タブのコンボボックスを更新
            for key, combo in self.plan_combos.items():
                if isinstance(combo, ttk.Combobox):
                    if key == 'ニーズ_本人':
                        templates = self.template_manager.get_templates('ニーズ', '本人')
                    elif key == 'ニーズ_保護者':
                        templates = self.template_manager.get_templates('ニーズ', '保護者')
                    elif key == '目標':
                        templates = self.template_manager.get_templates('目標', '短期')
                    elif key.startswith('方法_'):
                        method_type = key.split('_')[1]
                        templates = self.template_manager.get_templates('方法', method_type)
                    else:
                        templates = []
                    
                    if templates:
                        combo_values = [t[1] for t in templates]
                        combo['values'] = combo_values
            
            # 進路タブのコンボボックスを更新
            if hasattr(self, 'path_combo'):
                templates = self.template_manager.get_templates('進路')
                if templates:
                    try:
                        # get_templatesは (id, phrase) のタプルを返すので、t[1]がphrase
                        combo_values = [t[1] for t in templates if len(t) > 1]  # phrase column
                        if combo_values:
                            self.path_combo['values'] = combo_values
                        else:
                            self.path_combo['values'] = ["進路に関する内容を記入してください"]
                    except (IndexError, TypeError):
                        self.path_combo['values'] = ["進路に関する内容を記入してください"]
                    
        except Exception as e:
            print(f"テンプレート更新エラー: {e}")


