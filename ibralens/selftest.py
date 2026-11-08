"""فحص ذاتي يشتغل بعد البناء: يتأكد إن النماذج تشتغل والبحث بالعربي يعطي نتائج منطقية."""
import os
import sys
import tempfile
import traceback

import numpy as np
from PIL import Image, ImageDraw


def main(out_path):
    lines = []
    ok = True
    try:
        from ibralens.engine import create_engine, models_present
        from ibralens.paths import models_dir
        lines.append(f"models_dir={models_dir()} present={models_present()}")
        eng = create_engine(True)
        lines.append(f"device={eng.device}")
        # صورتين: شمس صفراء بسماء زرقاء، ونص/خطوط سوداء على أبيض
        a = Image.new("RGB", (320, 240), (90, 160, 235))
        ImageDraw.Draw(a).ellipse([200, 30, 280, 110], fill=(255, 220, 40))
        ImageDraw.Draw(a).rectangle([0, 180, 320, 240], fill=(60, 140, 50))
        b = Image.new("RGB", (320, 240), "white")
        d = ImageDraw.Draw(b)
        for y in range(20, 220, 18):
            d.line([20, y, 300, y], fill="black", width=4)
        ea, eb = eng.embed_image(a), eng.embed_image(b)
        ea2 = eng.embed_image(a.resize((160, 120)))
        lines.append(f"img self-sim (resized)={float(ea @ ea2):.3f}  cross={float(ea @ eb):.3f}")
        ok &= float(ea @ ea2) > 0.9
        for q in ("سماء زرقاء وشمس", "blue sky and sun", "طفل", "وشم", "سيارة"):
            t = eng.embed_text(q)
            lines.append(f"text '{q}': sky={float(t @ ea):.3f} lines={float(t @ eb):.3f}")
        t1 = eng.embed_text("سماء زرقاء وشمس")
        ok &= float(t1 @ ea) > float(t1 @ eb)
        ok &= abs(float(np.linalg.norm(t1)) - 1) < 1e-3
    except Exception:
        ok = False
        lines.append(traceback.format_exc())
    lines.append("SELFTEST " + ("OK" if ok else "FAIL"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "ibralens_selftest.txt")))
