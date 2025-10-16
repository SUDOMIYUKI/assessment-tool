from anthropic import Anthropic, APIError
import json
import re
import time
from .privacy import PrivacyProtector
from .prompts import SYSTEM_PROMPT, ASSESSMENT_PROMPT, REPORT_PROMPT
import config

class AIAnalyzer:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
        self.privacy = PrivacyProtector()
    
    def analyze_interview(self, interview_data):
        names_dict = {
            'child': interview_data['児童氏名'],
            'guardian': interview_data.get('保護者氏名', '')
        }
        
        anonymized_memo, reverse_map = self.privacy.anonymize_text(
            interview_data['メモ'],
            names_dict
        )
        
        assessment_data = self._generate_assessment_with_retry(
            anonymized_memo,
            interview_data
        )
        
        report_text = self._generate_report_with_retry(
            anonymized_memo,
            interview_data
        )
        
        report_text = self.privacy.restore_text(report_text, reverse_map)
        
        return {
            'assessment_data': assessment_data,
            'report_text': report_text,
            'missing_info': assessment_data.get('missing_info', [])
        }
    
    def _generate_assessment_with_retry(self, anonymized_memo, interview_data):
        for attempt in range(config.API_MAX_RETRIES):
            try:
                return self._generate_assessment(anonymized_memo, interview_data)
            except APIError as e:
                if "rate_limit" in str(e).lower() and attempt < config.API_MAX_RETRIES - 1:
                    wait_time = config.API_RETRY_DELAY * (attempt + 1)
                    print(f"⏳ レート制限により{wait_time}秒待機中...")
                    time.sleep(wait_time)
                else:
                    raise
            except json.JSONDecodeError as e:
                if attempt < config.API_MAX_RETRIES - 1:
                    print(f"⚠️ JSON解析失敗、リトライ中... ({attempt + 1}/{config.API_MAX_RETRIES})")
                    time.sleep(config.API_RETRY_DELAY)
                else:
                    return self._create_fallback_assessment()
        
        return self._create_fallback_assessment()
    
    def _generate_report_with_retry(self, anonymized_memo, interview_data):
        for attempt in range(config.API_MAX_RETRIES):
            try:
                return self._generate_report(anonymized_memo, interview_data)
            except APIError as e:
                if "rate_limit" in str(e).lower() and attempt < config.API_MAX_RETRIES - 1:
                    wait_time = config.API_RETRY_DELAY * (attempt + 1)
                    print(f"⏳ レート制限により{wait_time}秒待機中...")
                    time.sleep(wait_time)
                else:
                    raise
        
        return "報告書の生成に失敗しました。手動で作成してください。"
    
    def _generate_assessment(self, anonymized_memo, interview_data):
        medical_info = self._format_medical_info(interview_data.get('通院状況', {}))
        
        prompt = ASSESSMENT_PROMPT.format(
            memo=anonymized_memo,
            grade=interview_data['学年'],
            school=interview_data['学校名'],
            medical_info=medical_info
        )
        
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            timeout=config.API_TIMEOUT
        )
        
        result_text = response.content[0].text
        
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            assessment_data = json.loads(json_match.group())
        else:
            raise ValueError("AI応答からJSONを抽出できませんでした")
        
        return assessment_data
    
    def _generate_report(self, anonymized_memo, interview_data):
        medical_info = self._format_medical_info(interview_data.get('通院状況', {}))
        
        prompt = REPORT_PROMPT.format(
            memo=anonymized_memo,
            grade=interview_data['学年'],
            school=interview_data['学校名'],
            time=interview_data.get('面談時間', '未記録'),
            place=interview_data.get('面談場所', '未記録'),
            medical_info=medical_info
        )
        
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            timeout=config.API_TIMEOUT
        )
        
        return response.content[0].text
    
    def _format_medical_info(self, medical_info):
        if not medical_info or not medical_info.get('通院あり'):
            return "通院なし"
        
        text = f"{medical_info.get('病院名', '不明')}に通院中"
        if medical_info.get('診断名'):
            text += f"（診断名: {medical_info.get('診断名')}）"
        if medical_info.get('投薬'):
            text += f"、投薬: {medical_info.get('投薬')}"
        if medical_info.get('頻度'):
            text += f"、頻度: {medical_info.get('頻度')}"
        
        return text
    
    def _create_fallback_assessment(self):
        return {
            "issues": {
                "不登校": {"該当": False, "詳細": "メモから判断してください"},
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
            "future_path": {"type": "不明", "detail": ""},
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
            "missing_info": ["AI分析が失敗しました。手動で入力してください。"]
        }

