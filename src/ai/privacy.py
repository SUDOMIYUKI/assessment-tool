import pykakasi
import re

class PrivacyProtector:
    def __init__(self):
        self.kakasi = pykakasi.kakasi()
    
    def get_initials(self, full_name):
        if not full_name or full_name.strip() == "":
            return "X.X."
        
        try:
            result = self.kakasi.convert(full_name)
            initials = ""
            
            for item in result:
                if item['orig']:
                    hepburn = item.get('hepburn', '')
                    if hepburn:
                        initials += hepburn[0].upper() + "."
            
            if not initials or len(initials) < 2:
                name_cleaned = re.sub(r'[^ぁ-んァ-ヶー一-龯a-zA-Z]', '', full_name)
                if len(name_cleaned) >= 2:
                    initials = "A.B."
                else:
                    initials = "X.X."
            
            return initials
        
        except Exception as e:
            print(f"⚠️ イニシャル生成エラー: {e}")
            return "X.X."
    
    def anonymize_text(self, text, names_dict):
        anonymized = text
        reverse_map = {}
        
        for role, name in names_dict.items():
            if name and name.strip():
                initials = self.get_initials(name)
                anonymized = anonymized.replace(name, initials)
                reverse_map[initials] = name
        
        return anonymized, reverse_map
    
    def restore_text(self, text, reverse_map):
        restored = text
        for initials, name in reverse_map.items():
            restored = restored.replace(initials, name)
        return restored

