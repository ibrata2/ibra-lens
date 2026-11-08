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
}


class Settings(dict):
    def __init__(self):
        super().__init__(DEFAULTS)
        self.file = os.path.join(data_dir(), "settings.json")
        try:
            with open(self.file, encoding="utf-8") as f:
                self.update(json.load(f))
        except Exception:
            pass

    def save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(dict(self), f, ensure_ascii=False, indent=1)
        except Exception:
            pass
