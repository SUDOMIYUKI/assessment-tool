"""
OCR処理モジュール - 改善版
- 写真からテキストを抽出（画像前処理付き）
- チェックボックス認識の改善（■、☑、レ、×に対応）
- 信頼度スコアの算出
- 抽出したテキストをアセスメントデータに変換
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import os


class OCRProcessor:
    """OCR処理クラス（改善版）"""
    
    def __init__(self):
        """初期化"""
        # Tesseractのパスを自動検出・設定
        self._setup_tesseract_path()
        
        # OCR設定（日本語+英語対応）
        self.config = r'--oem 3 --psm 6 -l jpn+eng'
        
        # チェックボックスの認識パターン（四角形のみ）
        self.checkbox_patterns = {
            'checked': ['■', '☑', '✔', '×', 'レ'],
            'unchecked': ['□', '口']
        }
    
    def _setup_tesseract_path(self):
        """TesseractのPATHを自動設定"""
        # Windows標準インストールパス
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
        ]
        
        # 既にPATHが通っているかチェック
        try:
            pytesseract.get_tesseract_version()
            print("Tesseractが正常に検出されました")
            return
        except:
            pass
        
        # 可能なパスをチェック
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"Tesseractパスを設定: {path}")
                return
        
        # 見つからない場合の警告
        print("警告: Tesseract OCRが見つかりません")
        print("以下のいずれかの場所にインストールしてください：")
        for path in possible_paths[:2]:  # メジャーパスのみ表示
            print(f"  - {path}")
        
        raise FileNotFoundError("Tesseract OCRが見つかりません")
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        """
        手書き文字に最適化した高精度画像前処理
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            前処理済みの画像
        """
        print("高精度画像前処理開始...")
        
        # 画像を読み込み
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"画像を読み込めません: {image_path}")
        
        print(f"元画像サイズ: {img.shape}")
        
        # 大幅な画像拡大（OCR精度向上）
        height, width = img.shape[:2]
        if width < 3000:  # 幅が3000px未満なら拡大
            scale = 3000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            print(f"画像拡大: {new_width}x{new_height}")
        
        # グレースケール化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # ヒストグラム平坦化でコントラスト改善
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # ノイズ除去（より強力）
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # ガンマ補正で明度調整
        gamma = 1.2
        gamma_corrected = np.power(denoised / 255.0, gamma) * 255.0
        gamma_corrected = gamma_corrected.astype(np.uint8)
        
        # 複数の二値化手法を試して最適なものを選択
        # 1. Otsu法
        _, otsu = cv2.threshold(gamma_corrected, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 2. 適応的二値化
        adaptive = cv2.adaptiveThreshold(
            gamma_corrected, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 15, 8
        )
        
        # 3. 平均値による二値化
        mean_val = np.mean(gamma_corrected)
        _, mean_thresh = cv2.threshold(gamma_corrected, mean_val - 20, 255, cv2.THRESH_BINARY)
        
        # 最も文字が鮮明になる手法を選択（白ピクセル数で判定）
        otsu_white = np.sum(otsu == 255)
        adaptive_white = np.sum(adaptive == 255)
        mean_white = np.sum(mean_thresh == 255)
        
        # 適度な白ピクセル数（30-70%）の手法を選択
        total_pixels = otsu.shape[0] * otsu.shape[1]
        methods = [
            (otsu, otsu_white / total_pixels, "Otsu法"),
            (adaptive, adaptive_white / total_pixels, "適応的二値化"),
            (mean_thresh, mean_white / total_pixels, "平均値二値化")
        ]
        
        # 30-70%の範囲で最も適切な手法を選択
        best_method = None
        best_score = float('inf')
        
        for binary_img, white_ratio, method_name in methods:
            if 0.3 <= white_ratio <= 0.7:
                # 理想的な白ピクセル比率（50%）からの距離で評価
                score = abs(white_ratio - 0.5)
                if score < best_score:
                    best_score = score
                    best_method = (binary_img, method_name)
        
        # 適切な手法が見つからない場合は適応的二値化を使用
        if best_method is None:
            binary = adaptive
            method_name = "適応的二値化（デフォルト）"
        else:
            binary, method_name = best_method
        
        print(f"選択された二値化手法: {method_name}")
        
        # モルフォロジー処理で文字を整える
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)
        
        # 細線化で文字を細くする（手書き文字の太さを調整）
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open)
        
        # PIL Imageに変換
        pil_image = Image.fromarray(opened)
        
        # デバッグ用: 前処理済み画像を保存（コメントアウト）
        # try:
        #     debug_path = image_path.replace('.', '_debug_processed.')
        #     pil_image.save(debug_path)
        #     print(f"デバッグ用前処理済み画像を保存: {debug_path}")
        # except Exception as e:
        #     print(f"デバッグ画像保存エラー: {e}")
        
        print("高精度画像前処理完了")
        return pil_image
    
    def extract_text_from_image(self, image_path: str, preprocess: bool = True) -> Tuple[str, float]:
        """
        画像からテキストを抽出
        
        Args:
            image_path: 画像ファイルのパス
            preprocess: 前処理を実行するか
            
        Returns:
            (抽出されたテキスト, 信頼度スコア)
        """
        try:
            print(f"画像を読み込み: {image_path}")
            
            if preprocess:
                image = self.preprocess_image(image_path)
                print("画像前処理完了")
            else:
                image = Image.open(image_path)
                print("画像を開きました")
            
            # 手書き文字用の複数OCR設定で試行
            best_text = ""
            best_conf = 0.0
            
            # 手書き文字に最適化した設定
            ocr_configs = [
                # 手書き文字特化設定（PSM 8: 単語認識）
                {'psm': 8, 'oem': 1, 'lang': 'jpn', 'desc': '手書き日本語単語'},
                {'psm': 8, 'oem': 3, 'lang': 'jpn', 'desc': 'LSTM日本語単語'},
                
                # 行認識（PSM 7: 単一行）
                {'psm': 7, 'oem': 1, 'lang': 'jpn', 'desc': '手書き日本語行'},
                {'psm': 7, 'oem': 3, 'lang': 'jpn', 'desc': 'LSTM日本語行'},
                
                # ブロック認識（PSM 6: 一様ブロック）
                {'psm': 6, 'oem': 1, 'lang': 'jpn', 'desc': '手書き日本語ブロック'},
                {'psm': 6, 'oem': 3, 'lang': 'jpn', 'desc': 'LSTM日本語ブロック'},
                
                # スパーステキスト（PSM 11）
                {'psm': 11, 'oem': 1, 'lang': 'jpn', 'desc': '手書きスパース'},
                {'psm': 11, 'oem': 3, 'lang': 'jpn', 'desc': 'LSTMスパース'},
                
                # 混在言語
                {'psm': 6, 'oem': 3, 'lang': 'jpn+eng', 'desc': '日英混在'},
            ]
            
            for cfg in ocr_configs:
                # 手書き文字用の詳細設定
                config_params = [
                    f'--oem {cfg["oem"]}',
                    f'--psm {cfg["psm"]}',
                    f'-l {cfg["lang"]}',
                    '-c tessedit_pageseg_mode=' + str(cfg["psm"]),
                    '-c preserve_interword_spaces=1',
                    '-c tessedit_char_blacklist=',
                    '-c tessedit_char_unblacklist_format=',
                    '-c load_system_dawg=0',
                    '-c load_freq_dawg=0',
                    '-c load_unambig_dawg=0',
                    '-c load_punc_dawg=0',
                    '-c load_number_dawg=0',
                    '-c load_bigram_dawg=0',
                    '-c wordrec_enable_assoc=0',
                    '-c edges_max_children_per_outline=40',
                    '-c edges_max_children_layers=10',
                    '-c textord_min_linesize=2.5',
                ]
                config = ' '.join(config_params)
                try:
                    # OCR実行（詳細データ付き）
                    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                    
                    # テキストを抽出
                    text = pytesseract.image_to_string(image, config=config)
                    
                    # 信頼度スコアを計算（平均）
                    confidences = [float(conf) for conf in data['conf'] if conf != '-1']
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    
                    print(f"{cfg['desc']}: 抽出テキスト長={len(text)}, 信頼度={avg_confidence:.1f}%")
                    
                    # 日本語文字が含まれている場合は優遇
                    japanese_chars = len([c for c in text if ord(c) > 127])
                    bonus = japanese_chars * 0.1  # 日本語文字1文字につき0.1%ボーナス
                    
                    adjusted_conf = avg_confidence + bonus
                    
                    if adjusted_conf > best_conf and len(text.strip()) > 0:
                        best_text = text
                        best_conf = avg_confidence  # 元の信頼度を保存
                        print(f"  -> 最良結果更新 (調整後信頼度: {adjusted_conf:.1f}%)")
                        
                except Exception as e:
                    print(f"{cfg['desc']} でエラー: {e}")
                    continue
            
            if best_text.strip():
                print(f"最終結果: 信頼度={best_conf:.1f}%, 抽出長={len(best_text)}")
                print("=" * 30)
                print("抽出されたテキスト（最初の500文字）:")
                print(best_text[:500])
                print("=" * 30)
            else:
                print("警告: テキストが抽出されませんでした")
                
            return best_text, best_conf
            
        except Exception as e:
            print(f"OCRエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return "", 0.0
    
    def is_checkbox_checked(self, text: str) -> bool:
        """
        チェックボックスがチェックされているか判定（丸チェックボックス対応）
        
        Args:
            text: 判定するテキスト
            
        Returns:
            チェックされている場合True
        """
        if not text:
            return False
        
        # 明確にチェック済みの場合
        for pattern in self.checkbox_patterns['checked']:
            if pattern in text:
                print(f"チェック済みパターン検出: '{pattern}' in '{text[:20]}'")
                return True
        
        # 明確に未チェックの場合
        for pattern in self.checkbox_patterns['unchecked']:
            if pattern in text:
                print(f"未チェックパターン検出: '{pattern}' in '{text[:20]}'")
                return False
        
        # パターンが見つからない場合、デフォルトは未選択
        print(f"チェックボックスパターン未検出: '{text[:20]}'")
        return False
    
    def parse_handwriting_sheet(self, text: str) -> Dict:
        """
        手書き支援シートのテキストを解析してデータを抽出
        
        Args:
            text: OCRで抽出したテキスト
            
        Returns:
            解析されたデータの辞書
        """
        data = {
            'confidence_scores': {}  # 各項目の信頼度を保存
        }
        
        print("=" * 50)
        print("手書きシート解析開始")
        print("=" * 50)
        
        # 基本情報の抽出（手書きシート形式に対応）
        data['child_name'] = self._extract_field(text, r'記入日.*?児童氏名[：:\s]*(.+?)(?=保護者|学校|支援員|\n)')
        data['guardian_name'] = self._extract_field(text, r'保護者氏名[：:\s]*(.+?)(?=学校|支援員|\n)')
        data['school_name'] = self._extract_field(text, r'学校名[：:\s]*(.+?)(?=学年|性別|\n)')
        data['grade'] = self._extract_field(text, r'学年[：:\s]*(.+?)(?=性別|\n)')
        data['gender'] = self._extract_gender(text)
        data['supporter'] = self._extract_field(text, r'支援員[：:\s]*(.+?)(?=\n|ひとり親)')
        data['single_parent'] = self._extract_single_parent(text)
        
        print(f"基本情報: 児童={data.get('child_name')}, 学校={data.get('school_name')}")
        
        # 家族関係（ジェノグラム）の抽出
        data['family_genogram'] = self._extract_genogram(text)
        
        # ジェノグラム画像の切り出し機能は削除されました
        
        # 登校状況の抽出
        data['attendance'] = self._extract_attendance(text)
        print(f"登校状況: {data['attendance'].get('frequency')}")
        
        # 生活状況の抽出
        data['life_rhythm'] = self._extract_life_issues(text, 'リズム')
        data['life_habit'] = self._extract_life_issues(text, '習慣')
        data['outing'] = self._extract_outing(text)
        print(f"生活状況: リズム={len(data['life_rhythm'])}項目, 習慣={len(data['life_habit'])}項目")
        
        # 学習状況の抽出
        data['study_issues'] = self._extract_study_issues(text)
        print(f"学習状況: {len(data['study_issues'])}項目")
        
        # 対人関係の抽出
        data['social_issues'] = self._extract_social_issues(text)
        print(f"対人関係: {len(data['social_issues'])}項目")
        
        # 発達特性・医療情報の抽出
        data['developmental'] = self._extract_developmental(text)
        data['medical_info'] = self._extract_medical_info(text)
        print(f"発達特性: {data['developmental'].get('has_issues', False)}")
        
        # 家庭環境の抽出
        data['family_issues'] = self._extract_family_issues(text)
        print(f"家庭環境: {len(data['family_issues'])}項目")
        
        # ニーズ・目標の抽出
        data['short_term_plan'] = self._extract_plan(text, '短期目標')
        data['long_term_plan'] = self._extract_plan(text, '長期目標')
        print(f"目標: 短期={bool(data['short_term_plan'])}, 長期={bool(data['long_term_plan'])}")
        
        # 支援への希望の抽出
        data['support_wishes'] = self._extract_support_wishes(text)
        print(f"支援希望: {len(data['support_wishes'])}項目")
        
        # 当日の様子の抽出
        data['memo'] = self._extract_memo(text)
        
        print("=" * 50)
        print("解析完了")
        print("=" * 50)
        
        return data
    
    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """テキストからフィールドを抽出"""
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            value = match.group(1).strip()
            # 不要な文字を削除
            value = re.sub(r'[_\-\.]+', '', value)
            value = value.strip()
            return value if value else None
        return None
    
    def _extract_gender(self, text: str) -> Optional[str]:
        """性別を抽出（改善版）"""
        print(f"性別抽出開始: テキスト長={len(text)}")
        
        # 性別関連の行を探す
        lines = text.split('\n')
        gender_lines = []
        
        for i, line in enumerate(lines):
            # 性別、男性、女性を含む行を収集
            if any(keyword in line for keyword in ['性別', '男性', '女性', '男', '女']):
                gender_lines.append((i, line))
                print(f"性別関連行 {i}: '{line}'")
        
        # チェックボックスパターンで判定
        for line_num, line in gender_lines:
            # チェック済みパターンを確認
            if self.is_checkbox_checked(line):
                if any(male_word in line for male_word in ['男性', '男']):
                    print(f"男性チェック検出: '{line}'")
                    return '男性'
                elif any(female_word in line for female_word in ['女性', '女']):
                    print(f"女性チェック検出: '{line}'")
                    return '女性'
        
        # パターンマッチングで判定（チェックボックスが認識できない場合）
        gender_patterns = [
            (r'■.*?男性|男性.*?■', '男性'),
            (r'■.*?女性|女性.*?■', '女性'),
            (r'☑.*?男性|男性.*?☑', '男性'),
            (r'☑.*?女性|女性.*?☑', '女性'),
            (r'×.*?男性|男性.*?×', '男性'),
            (r'×.*?女性|女性.*?×', '女性'),
        ]
        
        for pattern, gender in gender_patterns:
            if re.search(pattern, text):
                print(f"パターンマッチ検出: {gender} (パターン: {pattern})")
                return gender
        
        print("性別を特定できませんでした")
        return None
    
    def _extract_single_parent(self, text: str) -> bool:
        """ひとり親世帯かどうかを抽出"""
        lines = text.split('\n')
        for line in lines:
            if 'ひとり親' in line:
                if self.is_checkbox_checked(line) and '該当' in line and '非該当' not in line:
                    return True
        return False
    
    def _extract_genogram(self, text: str) -> Dict:
        """ジェノグラム情報を抽出"""
        genogram = {
            'raw_text': '',
            'notes': ''
        }
        
        # ジェノグラムセクションを特定
        section_match = re.search(r'家族関係.*?ジェノグラム(.*?)(?=【|登校状況)', text, re.DOTALL)
        if section_match:
            section_text = section_match.group(1)
            genogram['raw_text'] = section_text.strip()
            
            # 特記事項を抽出
            notes_match = re.search(r'特記事項[：:\s]*(.*?)(?=\n\n|$)', section_text, re.DOTALL)
            if notes_match:
                genogram['notes'] = notes_match.group(1).strip()
        
        return genogram
    
    def _extract_attendance(self, text: str) -> Dict:
        """登校状況を抽出（改善版）"""
        print("登校状況抽出開始")
        attendance_data = {}
        
        lines = text.split('\n')
        
        # 登校頻度の選択肢を探す
        frequency_options = ['週0回', '週1-2回', '週3-4回', 'ほぼ毎日']
        frequency_patterns = [
            (r'週0', '週0回'),
            (r'週1[-\-]?2|週1.2', '週1-2回'), 
            (r'週3[-\-]?4|週3.4', '週3-4回'),
            (r'ほぼ毎日|毎日', 'ほぼ毎日')
        ]
        
        print("登校頻度チェック:")
        for i, line in enumerate(lines):
            if any(freq in line for freq in ['週0', '週1', '週2', '週3', '週4', '毎日']):
                print(f"  行 {i}: '{line}'")
                
                # チェックボックスが選択されているかチェック
                if self.is_checkbox_checked(line):
                    for pattern, freq_name in frequency_patterns:
                        if re.search(pattern, line):
                            attendance_data['frequency'] = freq_name
                            print(f"  -> 選択された頻度: {freq_name}")
                            break
        
        # 不登校の該当チェック
        print("不登校該当チェック:")
        for i, line in enumerate(lines):
            if '不登校' in line:
                print(f"  行 {i}: '{line}'")
                if self.is_checkbox_checked(line):
                    if '該当' in line and '非該当' not in line:
                        attendance_data['truancy'] = True
                        print("  -> 不登校該当: True")
                    elif '非該当' in line:
                        attendance_data['truancy'] = False
                        print("  -> 不登校該当: False")
        
        # デフォルト値設定（何も選択されていない場合）
        if 'frequency' not in attendance_data:
            attendance_data['frequency'] = None
            print("  -> 登校頻度: 未選択")
        
        if 'truancy' not in attendance_data:
            attendance_data['truancy'] = False
            print("  -> 不登校該当: デフォルト False")
        
        # 詳細・経緯
        detail_match = re.search(r'登校状況.*?詳細[：:\s]*(.*?)(?=【|生活状況)', text, re.DOTALL)
        if detail_match:
            attendance_data['detail'] = detail_match.group(1).strip()
        
        return attendance_data
    
    def _extract_life_issues(self, text: str, category: str) -> List[str]:
        """生活状況の課題を抽出"""
        checked = []
        
        issue_map = {
            'リズム': ['朝起きられない', '昼夜逆転', '睡眠不足'],
            '習慣': ['食事の乱れ', '運動不足', 'ゲーム依存']
        }
        
        if category not in issue_map:
            return checked
        
        lines = text.split('\n')
        for line in lines:
            if category in line:
                for issue in issue_map[category]:
                    if issue in line and self.is_checkbox_checked(line):
                        checked.append(issue)
        
        return checked
    
    def _extract_outing(self, text: str) -> str:
        """外出状況を抽出"""
        lines = text.split('\n')
        for line in lines:
            if '外出' in line:
                if self.is_checkbox_checked(line):
                    if 'する' in line and 'しない' not in line:
                        return '外出する'
                    elif 'コンビニ' in line:
                        return 'コンビニ程度'
                    elif 'しない' in line:
                        return 'ほぼ外出しない'
        return ''
    
    def _extract_study_issues(self, text: str) -> List[str]:
        """学習状況の課題を抽出"""
        checked = []
        issues = ['学習の遅れ', '低学力', '習慣なし', '環境なし']
        
        lines = text.split('\n')
        for line in lines:
            if '学習' in line:
                for issue in issues:
                    if issue in line and self.is_checkbox_checked(line):
                        checked.append(issue)
        
        return checked
    
    def _extract_social_issues(self, text: str) -> List[str]:
        """対人関係の課題を抽出"""
        checked = []
        issues = ['対人緊張', '友達不安', 'コミュ苦手']
        
        lines = text.split('\n')
        for line in lines:
            if '対人' in line:
                for issue in issues:
                    if issue in line and self.is_checkbox_checked(line):
                        checked.append(issue)
        
        return checked
    
    def _extract_developmental(self, text: str) -> Dict:
        """発達特性を抽出"""
        developmental = {
            'has_issues': False,
            'detail': ''
        }
        
        lines = text.split('\n')
        for line in lines:
            if '発達特性' in line and self.is_checkbox_checked(line):
                developmental['has_issues'] = True
                # 内容を抽出
                detail_match = re.search(r'内容[：:\s]*([^）]+)', line)
                if detail_match:
                    developmental['detail'] = detail_match.group(1).strip()
                break
        
        return developmental
    
    def _extract_medical_info(self, text: str) -> Dict:
        """医療情報を抽出"""
        medical = {
            'hospital': '',
            'frequency': '',
            'diagnosis': '',
            'medication': '',
            'handbook': ''
        }
        
        lines = text.split('\n')
        for line in lines:
            if '通院' in line and self.is_checkbox_checked(line):
                hospital_match = re.search(r'病院[：:\s]*([^頻]+)', line)
                if hospital_match:
                    medical['hospital'] = hospital_match.group(1).strip()
                freq_match = re.search(r'頻度[：:\s]*([^）]+)', line)
                if freq_match:
                    medical['frequency'] = freq_match.group(1).strip()
            
            if '診断' in line and self.is_checkbox_checked(line):
                diag_match = re.search(r'名称[：:\s]*([^）]+)', line)
                if diag_match:
                    medical['diagnosis'] = diag_match.group(1).strip()
            
            if '投薬' in line and self.is_checkbox_checked(line):
                med_match = re.search(r'薬名[：:\s]*([^）]+)', line)
                if med_match:
                    medical['medication'] = med_match.group(1).strip()
            
            if '手帳' in line and self.is_checkbox_checked(line):
                handbook_match = re.search(r'種類[：:\s]*([^）]+)', line)
                if handbook_match:
                    medical['handbook'] = handbook_match.group(1).strip()
        
        return medical
    
    def _extract_family_issues(self, text: str) -> List[str]:
        """家庭環境の課題を抽出"""
        checked = []
        issues = ['経済困難', '家族関係', '他世帯員', '虐待', 'その他']
        
        lines = text.split('\n')
        for line in lines:
            if '家庭環境' in line or '課題' in line:
                for issue in issues:
                    if issue in line and self.is_checkbox_checked(line):
                        checked.append(issue)
        
        return checked
    
    def _extract_plan(self, text: str, plan_type: str) -> Dict:
        """支援計画を抽出"""
        plan = {}
        
        # セクションを特定
        section_match = re.search(f'{plan_type}(.*?)(?=【|支援への希望|当日の様子|$)', text, re.DOTALL)
        if not section_match:
            return plan
        
        section_text = section_match.group(1)
        
        # 各フィールドを抽出
        fields = {
            '課題': 'issue',
            '現状': 'current_status',
            'ニーズ本人': 'needs_child',
            'ニーズ保護者': 'needs_guardian',
            '目標': 'goal',
            '方法': 'method'
        }
        
        for jp_field, en_field in fields.items():
            match = re.search(rf'{jp_field}[：:\s]*(.*?)(?=課題|現状|ニーズ|目標|方法|$)', section_text, re.DOTALL)
            if match:
                value = match.group(1).strip()
                if value:
                    plan[en_field] = value
        
        return plan
    
    def _extract_support_wishes(self, text: str) -> Dict:
        """支援への希望を抽出"""
        wishes = {}
        
        # 希望の曜日
        days = ['月', '火', '水', '木', '金']
        selected_days = []
        lines = text.split('\n')
        for line in lines:
            if '曜日' in line:
                for day in days:
                    if day in line and self.is_checkbox_checked(line):
                        selected_days.append(day)
        if selected_days:
            wishes['preferred_days'] = '・'.join(selected_days)
        
        # 希望の時間帯
        time_match = re.search(r'時間[：:\s]*(.*?)(?=\n|場所)', text)
        if time_match:
            wishes['preferred_time'] = time_match.group(1).strip()
        
        # 希望の場所
        location_match = re.search(r'場所[：:\s]*(.*?)(?=\n|支援員)', text)
        if location_match:
            wishes['preferred_location'] = location_match.group(1).strip()
        
        # 支援員希望
        staff_match = re.search(r'支援員希望[：:\s]*(.*?)(?=\n|解決)', text, re.DOTALL)
        if staff_match:
            wishes['preferred_staff'] = staff_match.group(1).strip()
        
        # 解決したいこと
        goal_match = re.search(r'解決したいこと[：:\s]*(.*?)(?=【|当日の様子|$)', text, re.DOTALL)
        if goal_match:
            wishes['solving_goals'] = goal_match.group(1).strip()
        
        return wishes
    
    def _extract_memo(self, text: str) -> str:
        """当日の様子・メモを抽出"""
        memo_match = re.search(r'当日の様子.*?メモ[：:\s]*(.*?)$', text, re.DOTALL)
        if memo_match:
            return memo_match.group(1).strip()
        return ''


if __name__ == '__main__':
    # テスト用
    processor = OCRProcessor()
    
    # 画像ファイルのパスを指定
    image_path = 'test_image.jpg'
    
    if Path(image_path).exists():
        text, confidence = processor.extract_text_from_image(image_path)
        print("=" * 50)
        print("抽出されたテキスト:")
        print("=" * 50)
        print(text)
        print(f"\n信頼度: {confidence:.1f}%")
        
        print("\n" + "=" * 50)
        print("解析されたデータ:")
        print("=" * 50)
        data = processor.parse_handwriting_sheet(text)
        
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"画像ファイルが見つかりません: {image_path}")

