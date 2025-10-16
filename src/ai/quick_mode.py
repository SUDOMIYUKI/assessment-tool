from src.database.templates import TemplateManager

class QuickModeAnalyzer:
    def __init__(self):
        self.template_manager = TemplateManager()
    
    def create_from_template(self, selected_templates):
        """
        選択されたテンプレートからアセスメントデータを生成
        
        selected_templates: {
            'issues': {issue_name: detail_text, ...},
            'short_term_plan': {
                'ニーズ_本人': text,
                'ニーズ_保護者': text,
                '目標': text,
                '方法': text
            },
            'future_path': {
                'type': '進学' or '就職',
                'detail': text
            }
        }
        """
        
        # デフォルト構造
        assessment_data = {
            "issues": {
                "不登校": {"該当": False, "詳細": ""},
                "引きこもり": {"該当": False, "詳細": ""},
                "生活リズム": {"該当": False, "詳細": ""},
                "生活習慣": {"該当": False, "詳細": ""},
                "学習の遅れ・低学力": {"該当": False, "詳細": ""},
                "学習習慣・環境": {"該当": False, "詳細": ""},
                "発達特性or発達課題": {"該当": False, "詳細": ""},
                "対人緊張の高さ": {"該当": False, "詳細": ""},
                "コミュニケーションに苦手意識": {"該当": False, "詳細": ""},
                "家庭環境": {"該当": False, "詳細": ""},
                "虐待": {"該当": False, "詳細": ""},
                "他の世帯員の問題": {"該当": False, "詳細": ""},
                "その他": {"該当": False, "詳細": ""}
            },
            "future_path": {
                "type": "不明",
                "detail": ""
            },
            "short_term_plan": {
                "課題": "",
                "現状": "",
                "ニーズ_本人": "",
                "ニーズ_保護者": "",
                "目標": "",
                "方法": ""
            },
            "long_term_plan": {
                "課題": "",
                "現状": "",
                "ニーズ_本人": "",
                "ニーズ_保護者": "",
                "目標": "",
                "方法": ""
            },
            "missing_info": []
        }
        
        # 選択された課題を反映
        if 'issues' in selected_templates:
            for issue_name, detail in selected_templates['issues'].items():
                if issue_name in assessment_data['issues']:
                    assessment_data['issues'][issue_name] = {
                        "該当": True,
                        "詳細": detail
                    }
        
        # 進路を反映
        if 'future_path' in selected_templates:
            assessment_data['future_path'] = selected_templates['future_path']
        
        # 短期計画を反映
        if 'short_term_plan' in selected_templates:
            assessment_data['short_term_plan'].update(selected_templates['short_term_plan'])
        
        # 長期計画を反映
        if 'long_term_plan' in selected_templates:
            assessment_data['long_term_plan'].update(selected_templates['long_term_plan'])
        
        return assessment_data
    
    def generate_simple_report(self, interview_data, assessment_data):
        """簡易報告書を生成"""
        
        report_parts = []
        
        # ヘッダー
        report_parts.append("【時間】")
        report_parts.append(interview_data.get('面談時間', '未記録'))
        report_parts.append("")
        
        report_parts.append("【支援内容】")
        report_parts.append("初回アセスメント")
        report_parts.append("")
        
        # 面談内容（元のメモ）
        report_parts.append("【面談内容】")
        report_parts.append(interview_data.get('メモ', ''))
        report_parts.append("")
        
        # 課題まとめ
        report_parts.append("【確認された課題】")
        issues = assessment_data.get('issues', {})
        for issue_name, issue_data in issues.items():
            if issue_data.get('該当'):
                detail = issue_data.get('詳細', '')
                if detail:
                    report_parts.append(f"・{issue_name}：{detail}")
                else:
                    report_parts.append(f"・{issue_name}")
        report_parts.append("")
        
        # 本人情報
        report_parts.append("【本人情報】")
        report_parts.append(f"・{interview_data.get('学校名', '')} {interview_data.get('学年', '')}年生")
        
        medical_info = interview_data.get('通院状況', {})
        medical_items = []
        
        if medical_info.get('通院あり'):
            hospital_text = medical_info.get('病院名', '不明')
            if medical_info.get('頻度'):
                hospital_text += f"（{medical_info.get('頻度')}）"
            medical_items.append(f"通院：{hospital_text}")
        
        if medical_info.get('投薬治療'):
            medical_items.append(f"投薬治療：{medical_info.get('薬名', '不明')}")
        
        if medical_info.get('診断あり'):
            medical_items.append(f"診断：{medical_info.get('診断名', '不明')}")
        
        if medical_info.get('手帳あり'):
            medical_items.append(f"手帳：{medical_info.get('手帳種類', '不明')}")
        
        if medical_items:
            for item in medical_items:
                report_parts.append(f"・{item}")
        else:
            report_parts.append("・医療・支援情報：なし")
        report_parts.append("")
        
        # 支援希望
        support_wishes = interview_data.get('支援希望', {})
        if support_wishes and any(support_wishes.values()):
            report_parts.append("【支援への希望】")
            if support_wishes.get('希望の曜日'):
                report_parts.append(f"・希望の曜日：{support_wishes.get('希望の曜日')}")
            if support_wishes.get('希望の時間帯'):
                report_parts.append(f"・希望の時間帯：{support_wishes.get('希望の時間帯')}")
            if support_wishes.get('希望の場所'):
                report_parts.append(f"・希望の場所：{support_wishes.get('希望の場所')}")
            if support_wishes.get('希望の支援員'):
                report_parts.append(f"・希望の支援員：{support_wishes.get('希望の支援員')}")
            if support_wishes.get('解決したいこと'):
                report_parts.append(f"・解決したいこと：{support_wishes.get('解決したいこと')}")
            report_parts.append("")
        
        # 支援計画
        report_parts.append("【支援計画（短期目標）】")
        plan = assessment_data.get('short_term_plan', {})
        if plan.get('目標'):
            report_parts.append(f"目標：{plan.get('目標')}")
        if plan.get('方法'):
            report_parts.append(f"方法：{plan.get('方法')}")
        report_parts.append("")
        
        # 次回予定
        report_parts.append("【次回の予定】")
        report_parts.append("次回面談日を調整予定")
        
        return "\n".join(report_parts)


