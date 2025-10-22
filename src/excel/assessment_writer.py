import openpyxl
from datetime import datetime
from pathlib import Path

class AssessmentWriter:
    def __init__(self, template_path='templates/アセスメントシート原本.xlsx'):
        self.template_path = Path(template_path)
    
    def create_assessment_file(self, interview_data, assessment_data, output_path):
        if not self.template_path.exists():
            raise FileNotFoundError(
                f"テンプレートファイルが見つかりません: {self.template_path}\n"
                "templates/ディレクトリにアセスメントシート原本.xlsxを配置してください"
            )
        
        try:
            wb = openpyxl.load_workbook(str(self.template_path))
            # シート名を確認
            sheet_names = wb.sheetnames
            print(f"利用可能なシート名: {sheet_names}")
            
            # 1枚目のシートに元のテンプレート形式を維持しながらデータを入力
            # アセスメントシートまたは類似の名前を探す
            target_sheet = None
            for sheet_name in sheet_names:
                if 'アセスメント' in sheet_name or 'assessment' in sheet_name.lower():
                    target_sheet = sheet_name
                    break
            
            if not target_sheet:
                # 最初のシートを使用
                target_sheet = sheet_names[0]
                print(f"アセスメントシートが見つからないため、最初のシート '{target_sheet}' を使用します")
            
            ws = wb[target_sheet]
            print(f"1枚目のシート '{target_sheet}' にデータを入力します（元のテンプレート形式を維持）")
            
            # テンプレートファイルの内容をデバッグ出力
            print(f"🔧 デバッグ: テンプレートファイルの内容を確認します")
            for row in range(10, 20):  # 課題セクションの行を確認
                for col in ['B', 'I']:  # 課題セクションの列を確認
                    cell_address = f"{col}{row}"
                    cell_value = ws[cell_address].value
                    print(f"🔧 デバッグ: {cell_address} = '{cell_value}'")
            
            # 基本情報の入力
            self._fill_basic_info(ws, interview_data)
            
            # 世帯の具体的な課題の入力
            self._fill_household_issues(ws, assessment_data)
            
            # 希望する進路の入力
            self._fill_future_path(ws, assessment_data, interview_data)
            
            # 支援計画の入力
            self._fill_support_plans(ws, assessment_data)
            
        except Exception as e:
            raise ValueError(f"テンプレートファイルの読み込みエラー: {str(e)}")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(str(output_path))
        print(f"✅ アセスメントシートを作成: {output_path}")
        
        return str(output_path)
    
    def _fill_basic_info(self, ws, interview_data):
        """基本情報を入力"""
        # 支援番号（日付ベース）
        if '面談実施日' in interview_data and interview_data['面談実施日']:
            date_obj = interview_data['面談実施日']
            if isinstance(date_obj, datetime):
                support_number = date_obj.strftime('%Y%m%d')
            else:
                support_number = date_obj
            ws['C3'] = support_number
        
        # 担当支援員
        ws['G3'] = interview_data.get('担当支援員', '')
        
        # 面談実施日
        if '面談実施日' in interview_data and interview_data['面談実施日']:
            date_obj = interview_data['面談実施日']
            if isinstance(date_obj, datetime):
                ws['H3'] = date_obj.strftime('%m月%d日')
            else:
                ws['H3'] = date_obj
        
        # 世帯主氏名（保護者氏名）
        ws['C4'] = interview_data.get('保護者氏名', '')
        
        # 児童氏名
        ws['G4'] = interview_data.get('児童氏名', '')
        
        # 性別
        ws['O4'] = interview_data.get('性別', '')
        
        # 学校名
        ws['C5'] = interview_data.get('学校名', '')
        
        # 学年
        ws['I5'] = str(interview_data.get('学年', ''))
        
        # ひとり親世帯
        ws['N5'] = interview_data.get('ひとり親世帯', '該当しない')
    
    def _fill_household_issues(self, ws, assessment_data):
        """世帯の具体的な課題を入力"""
        issues_data = assessment_data.get('issues', {})
        
        # 各課題項目のチェックボックスと詳細を設定
        issue_mappings = {
            '不登校': {'row': 11, 'col': 'B'},
            '引きこもり': {'row': 11, 'col': 'I'},
            '生活リズム': {'row': 12, 'col': 'B'},
            '生活習慣': {'row': 12, 'col': 'I'},
            '学習の遅れ・低学力': {'row': 13, 'col': 'B'},
            '学習習慣・環境': {'row': 13, 'col': 'I'},
            '発達特性or発達課題': {'row': 14, 'col': 'B'},
            '対人緊張の高さ': {'row': 14, 'col': 'I'},
            'コミュニケーションに苦手意識': {'row': 15, 'col': 'B'},
            '家庭環境': {'row': 15, 'col': 'I'},
            '虐待': {'row': 16, 'col': 'B'},
            'その他': {'row': 16, 'col': 'I'}
        }
        
        for issue_name, mapping in issue_mappings.items():
            if issue_name in issues_data:
                issue_data = issues_data[issue_name]
                checkbox = "■" if issue_data.get('該当', False) else "□"
                detail = issue_data.get('詳細', '')
                
                # 既存のセル内容を取得
                cell_address = f"{mapping['col']}{mapping['row']}"
                existing_value = ws[cell_address].value or ""
                
                print(f"🔧 デバッグ: {cell_address} の既存内容: '{existing_value}'")
                print(f"🔧 デバッグ: {cell_address} の新しい内容: '{checkbox}{issue_name}({detail})'")
                
                # テンプレートのフォーマットを保持しながら、チェックボックスと詳細のみ更新
                if existing_value and existing_value.strip():
                    # 既存内容がある場合は、チェックボックスと詳細のみ更新
                    existing_text = str(existing_value)
                    
                    # チェックボックス部分のみを更新（既存の詳細部分は保持）
                    if existing_text.startswith('□') or existing_text.startswith('■'):
                        # 既存のチェックボックスを新しいものに置換
                        # 既存の詳細部分を抽出
                        if '(' in existing_text and ')' in existing_text:
                            # 既存の詳細部分を抽出
                            start_idx = existing_text.find('(')
                            end_idx = existing_text.rfind(')')
                            if start_idx != -1 and end_idx != -1:
                                existing_detail = existing_text[start_idx:end_idx+1]
                                # チェックボックスのみを更新し、既存の詳細部分は保持
                                new_value = f"{checkbox}{issue_name}{existing_detail}"
                            else:
                                # 詳細部分がない場合は、新しい詳細を追加
                                if detail and detail.strip():
                                    new_value = f"{checkbox}{issue_name}({detail})"
                                else:
                                    new_value = f"{checkbox}{issue_name}"
                        else:
                            # 詳細部分がない場合は、新しい詳細を追加
                            if detail and detail.strip():
                                new_value = f"{checkbox}{issue_name}({detail})"
                            else:
                                new_value = f"{checkbox}{issue_name}"
                    else:
                        # チェックボックスがない場合は、新しい内容を設定
                        if detail and detail.strip():
                            new_value = f"{checkbox}{issue_name}({detail})"
                        else:
                            new_value = f"{checkbox}{issue_name}"
                    
                    # セルに新しい値を設定
                    ws[cell_address] = new_value
                else:
                    # 既存内容がない場合は、テンプレートのフォーマットを保持しない
                    # セルを更新しない（既存のテンプレート形式を保持）
                    print(f"🔧 デバッグ: {cell_address} は既存内容がないため、更新をスキップします")
                    continue
    
    def _fill_future_path(self, ws, assessment_data, interview_data):
        """希望する進路を入力"""
        future_path = assessment_data.get('future_path', {})
        
        # 確認日
        if '面談実施日' in interview_data and interview_data['面談実施日']:
            date_obj = interview_data['面談実施日']
            if isinstance(date_obj, datetime):
                confirm_date = date_obj.strftime('%Y/%m/%d')
            else:
                confirm_date = date_obj
        else:
            confirm_date = ''
        
        # 進学・就職のチェックボックス
        path_type = future_path.get('type', '')
        checkbox_進学 = "■" if path_type == "進学" else "□"
        checkbox_就職 = "■" if path_type == "就職" else "□"
        
        # 具体的内容
        detail = future_path.get('detail', '')
        
        # B18セルに進路情報を設定（既存内容を保持）
        existing_value = ws['B18'].value or ""
        
        # 既存内容を保持しつつ、進路情報のみ更新
        if confirm_date or detail or path_type:
            # 進路情報を既存内容に追加
            path_info = f"確認日　{confirm_date}　{checkbox_進学}進学　　{checkbox_就職}就職（具体的内容）・{detail}"
            
            # 既存内容がある場合は結合、ない場合は新規作成
            if existing_value and existing_value.strip():
                new_value = f"{existing_value}\n{path_info}"
            else:
                new_value = path_info
            
            ws['B18'] = new_value
    
    def _fill_support_plans(self, ws, assessment_data):
        """支援計画を入力"""
        # 短期目標（支援計画）
        short_term_plan = assessment_data.get('short_term_plan', {})
        self._fill_support_plan_table(ws, short_term_plan, start_row=29)
        
        # 長期目標（本事業における達成目標）
        long_term_plan = assessment_data.get('long_term_plan', {})
        self._fill_support_plan_table(ws, long_term_plan, start_row=35)
    
    def _fill_support_plan_table(self, ws, plan_data, start_row):
        """支援計画テーブルを入力（既存内容を保持）"""
        # 課題
        existing_課題 = ws[f'B{start_row}'].value or ""
        new_課題 = plan_data.get('課題', '')
        if new_課題 and new_課題.strip():
            if existing_課題 and existing_課題.strip():
                ws[f'B{start_row}'] = f"{existing_課題}\n{new_課題}"
            else:
                ws[f'B{start_row}'] = new_課題
        
        # 現状
        existing_現状 = ws[f'D{start_row}'].value or ""
        new_現状 = plan_data.get('現状', '')
        if new_現状 and new_現状.strip():
            if existing_現状 and existing_現状.strip():
                ws[f'D{start_row}'] = f"{existing_現状}\n{new_現状}"
            else:
                ws[f'D{start_row}'] = new_現状
        
        # ニーズ（本人）
        existing_ニーズ_本人 = ws[f'F{start_row}'].value or ""
        new_ニーズ_本人 = plan_data.get('ニーズ_本人', '')
        if new_ニーズ_本人 and new_ニーズ_本人.strip():
            if existing_ニーズ_本人 and existing_ニーズ_本人.strip():
                ws[f'F{start_row}'] = f"{existing_ニーズ_本人}\n{new_ニーズ_本人}"
            else:
                ws[f'F{start_row}'] = new_ニーズ_本人
        
        # ニーズ（保護者）
        existing_ニーズ_保護者 = ws[f'F{start_row + 1}'].value or ""
        new_ニーズ_保護者 = plan_data.get('ニーズ_保護者', '')
        if new_ニーズ_保護者 and new_ニーズ_保護者.strip():
            if existing_ニーズ_保護者 and existing_ニーズ_保護者.strip():
                ws[f'F{start_row + 1}'] = f"{existing_ニーズ_保護者}\n{new_ニーズ_保護者}"
            else:
                ws[f'F{start_row + 1}'] = new_ニーズ_保護者
        
        # 目標
        existing_目標 = ws[f'J{start_row}'].value or ""
        new_目標 = plan_data.get('目標', '')
        if new_目標 and new_目標.strip():
            if existing_目標 and existing_目標.strip():
                ws[f'J{start_row}'] = f"{existing_目標}\n{new_目標}"
            else:
                ws[f'J{start_row}'] = new_目標
        
        # 具体的な方法
        existing_方法 = ws[f'N{start_row}'].value or ""
        new_方法 = plan_data.get('具体的な方法', '')
        if new_方法 and new_方法.strip():
            if existing_方法 and existing_方法.strip():
                ws[f'N{start_row}'] = f"{existing_方法}\n{new_方法}"
            else:
                ws[f'N{start_row}'] = new_方法