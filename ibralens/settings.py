import json
import os

from .paths import data_dir

DEFAULTS = {
    "roots": [],            # مجلدات/أقراص الفهرسة (فارغ = كل الأقراص)
    "exclude": [],
    "min_kb": 15,
    "min_side": 120,
    "use_gpu": True,
    "dup_threshold": 5,
    "results": 300,
    "auto_update_index": True,
    "check_updates": True,
    "lang": "ar",           # "ar" أو "en" — مستقلة عن لغة الوندوز
}


class Settings(dict):
    def __init__(self):
        super().__init__(DEFAULTS)
        self.file = os.path.join(data_dir(), "settings.json")
        saved = {}
        try:
            with open(self.file, encoding="utf-8") as f:
                saved = json.load(f)
        except Exception:
            pass
        if "lang" not in saved:
            # أول تشغيل: نستخدم اللغة اللي اخترتها بالمنصّب
            try:
                from .paths import base_dir
                with open(os.path.join(base_dir(), "defaults.ini"), encoding="utf-8", errors="ignore") as f:
                    if "lang=english" in f.read().replace(" ", "").lower():
                        saved["lang"] = "en"
            except Exception:
                pass
        self.update(saved)

    def save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(dict(self), f, ensure_ascii=False, indent=1)
        except Exception:
            pass
