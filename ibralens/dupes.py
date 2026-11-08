"""إيجاد الصور المكررة: متطابقة تماماً (نفس الملف) + متشابهة (نفس الصورة مصغرة/مضغوطة/معدلة قليلاً)."""
from collections import defaultdict

import numpy as np


class _UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        p = self.p
        p.setdefault(x, x)
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def find_duplicates(db, mode="similar", threshold=5):
    """mode: 'exact' أو 'similar'. يرجع قائمة مجموعات، كل مجموعة = قائمة معلومات صور."""
    rows = db.hashes()
    if not rows:
        return []
    uf = _UF()
    by_hash = defaultdict(list)
    for i, fh, ph, size in rows:
        if fh:
            by_hash[fh].append(i)
    for ids in by_hash.values():
        for x in ids[1:]:
            uf.union(ids[0], x)

    if mode == "similar":
        ids = np.array([r[0] for r in rows if r[2] is not None], np.int64)
        ph = np.array([r[2] for r in rows if r[2] is not None], np.int64).view(np.uint64)
        # فهرسة متعددة: نقسم البصمة 4 أجزاء × 16 بت، الصور المتشابهة تشترك بجزء واحد على الأقل
        for c in range(4):
            key = ((ph >> np.uint64(16 * c)) & np.uint64(0xFFFF)).astype(np.int64)
            order = np.argsort(key, kind="stable")
            k_sorted = key[order]
            bounds = np.flatnonzero(np.diff(k_sorted)) + 1
            for grp in np.split(order, bounds):
                if len(grp) < 2:
                    continue
                if len(grp) > 3000:  # بصمات فارغة (صور سادة) — نتجاهلها
                    continue
                hs = ph[grp]
                for a in range(len(grp) - 1):
                    d = np.bitwise_count(hs[a + 1:] ^ hs[a])
                    for b in np.flatnonzero(d <= threshold):
                        uf.union(int(ids[grp[a]]), int(ids[grp[a + 1 + b]]))

    groups = defaultdict(list)
    for i, *_ in rows:
        if i in uf.p:
            groups[uf.find(i)].append(i)
    groups = [g for g in groups.values() if len(g) > 1]
    if not groups:
        return []
    info = db.info([i for g in groups for i in g])
    exact_of = {i: fh for i, fh, _, _ in rows}
    out = []
    for g in groups:
        items = [info[i] for i in g if i in info]
        if len(items) < 2:
            continue
        # الأفضل أولاً: أكبر دقة ثم أكبر حجم
        items.sort(key=lambda d: (-(d["w"] or 0) * (d["h"] or 0), -(d["size"] or 0), len(d["path"])))
        for d in items:
            d["exact"] = exact_of.get(d["id"]) == exact_of.get(items[0]["id"])
        waste = sum(d["size"] or 0 for d in items[1:])
        out.append({"items": items, "waste": waste})
    out.sort(key=lambda g: -g["waste"])
    return out
