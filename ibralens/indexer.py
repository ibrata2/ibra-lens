"""فهرسة الصور: يمر على الأقراص/المجلدات، ويحسب بصمة الذكاء + البصمة المرئية + هاش الملف."""
import hashlib
import io
import os
import string
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

from .engine import open_image

IMAGE_EXT = {".jpg", ".jpeg", ".jfif", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".heic", ".heif"}

SKIP_DIRS = {
    "windows", "program files", "program files (x86)", "programdata", "$recycle.bin",
    "system volume information", "appdata", "node_modules", ".git", "__pycache__",
    "recovery", "$winreagent", "windowsapps", "$windows.~bt", "$windows.~ws", "msocache",
    "perflogs", "site-packages", ".cache", ".gradle", ".m2", "temp", "tmp",
}


def list_drives():
    if os.name != "nt":
        return [os.path.expanduser("~")]
    out = []
    for c in string.ascii_uppercase:
        p = f"{c}:\\"
        if os.path.exists(p):
            out.append(p)
    return out


def phash64(im):
    """بصمة مرئية 64 بت (DCT) — تتطابق للصور المصغرة/المضغوطة."""
    g = im.convert("L").resize((32, 32), Image.LANCZOS)
    a = np.asarray(g, np.float64)
    n = 32
    k = np.arange(n)
    C = np.cos(np.pi * (2 * k[None, :] + 1) * k[:, None] / (2 * n))
    d = C @ a @ C.T
    low = d[:8, :8].flatten()
    med = np.median(low[1:])
    bits = low > med
    v = 0
    for b in bits:
        v = (v << 1) | int(b)
    if v >= 2**63:
        v -= 2**64
    return v


class Indexer:
    def __init__(self, db, engine, settings, on_progress=None):
        self.db = db
        self.engine = engine
        self.s = settings
        self.on_progress = on_progress or (lambda d: None)
        self.stop_ev = threading.Event()
        self.pause_ev = threading.Event()
        self.thread = None
        self.state = {}

    @property
    def running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, roots):
        if self.running:
            return
        self.stop_ev.clear()
        self.pause_ev.clear()
        self.thread = threading.Thread(target=self._run, args=(list(roots),), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_ev.set()
        self.pause_ev.clear()

    def toggle_pause(self):
        if self.pause_ev.is_set():
            self.pause_ev.clear()
        else:
            self.pause_ev.set()
        return self.pause_ev.is_set()

    # ------------------------------------------------------------ walk
    def _walk(self, roots, exclude):
        exclude = [os.path.normcase(os.path.abspath(e)) for e in exclude if e]
        stack = list(roots)
        while stack and not self.stop_ev.is_set():
            d = stack.pop()
            if any(os.path.normcase(d).startswith(e) for e in exclude):
                continue
            try:
                with os.scandir(d) as it:
                    for e in it:
                        try:
                            if e.is_dir(follow_symlinks=False):
                                n = e.name.lower()
                                if n in SKIP_DIRS or n.startswith("$"):
                                    continue
                                stack.append(e.path)
                            elif e.is_file(follow_symlinks=False):
                                if os.path.splitext(e.name)[1].lower() in IMAGE_EXT:
                                    st = e.stat()
                                    yield e.path, st.st_size, st.st_mtime
                        except OSError:
                            continue
            except OSError:
                continue
            self.state["scanned_dirs"] = self.state.get("scanned_dirs", 0) + 1

    # ------------------------------------------------------------ load one
    def _load(self, item):
        path, size, mtime = item
        try:
            with open(path, "rb") as f:
                data = f.read()
            fh = hashlib.blake2b(data, digest_size=16).hexdigest()
            im = Image.open(io.BytesIO(data))
            w, h = im.size
            if min(w, h) < self.s.get("min_side", 120):
                return ("small", (path, size, mtime, w, h, None, None, None))
            im = open_image(io.BytesIO(data), max_side=1024)
            arr = self.engine.preprocess(im)
            ph = phash64(im)
            return ("ok", (path, size, mtime, w, h, fh, ph), arr)
        except Exception:
            return ("bad", path)

    # ------------------------------------------------------------ main
    def _run(self, roots):
        t0 = time.time()
        st = self.state = {"phase": "scan", "found": 0, "todo": 0, "done": 0, "skipped": 0,
                           "errors": 0, "removed": 0, "scanned_dirs": 0, "current": ""}
        self.on_progress(dict(st))
        known = self.db.known()
        min_bytes = int(self.s.get("min_kb", 15)) * 1024
        todo, seen = [], set()
        last = time.time()
        for path, size, mtime in self._walk(roots, self.s.get("exclude", [])):
            st["found"] += 1
            seen.add(path)
            if size < min_bytes:
                continue
            k = known.get(path)
            if k and k[0] == size and abs((k[1] or 0) - mtime) < 1:
                continue
            todo.append((path, size, mtime))
            if time.time() - last > 0.3:
                st["todo"] = len(todo)
                st["current"] = os.path.dirname(path)
                self.on_progress(dict(st))
                last = time.time()
        if self.stop_ev.is_set():
            st["phase"] = "stopped"
            self.on_progress(dict(st))
            return

        # حذف الصور اللي انمسحت من الحاسبة (ضمن المجلدات المفهرسة فقط)
        nroots = [os.path.normcase(r) for r in roots]
        gone = [p for p in known if p not in seen and any(os.path.normcase(p).startswith(r) for r in nroots)
                and not os.path.exists(p)]
        self.db.remove_paths(gone)
        st["removed"] = len(gone)

        st["phase"] = "index"
        st["todo"] = len(todo)
        self.on_progress(dict(st))
        batch_n = 32 if getattr(self.engine, "device", "CPU").startswith("GPU") else 16
        workers = max(2, min(8, (os.cpu_count() or 4)))
        rows, arrs, pend = [], [], []

        def flush():
            if not arrs:
                return
            embs = self.engine.embed_arrays(arrs).astype(np.float16)
            out = [r + (embs[i].tobytes(),) for i, r in enumerate(rows)]
            pend.extend(out)
            rows.clear()
            arrs.clear()
            if len(pend) >= 256:
                self.db.upsert_many(pend)
                pend.clear()

        def bounded(ex):
            # نخلي عدد محدود من الصور بالذاكرة حتى ما تمتلي الرام
            from collections import deque
            q = deque()
            it = iter(todo)
            for item in it:
                q.append(ex.submit(self._load, item))
                if len(q) >= workers * 8:
                    break
            while q:
                yield q.popleft().result()
                nxt = next(it, None)
                if nxt is not None:
                    q.append(ex.submit(self._load, nxt))

        with ThreadPoolExecutor(workers) as ex:
            for res in bounded(ex):
                while self.pause_ev.is_set() and not self.stop_ev.is_set():
                    time.sleep(0.2)
                if self.stop_ev.is_set():
                    break
                if res[0] == "ok":
                    rows.append(res[1])
                    arrs.append(res[2])
                    if len(arrs) >= batch_n:
                        try:
                            flush()
                        except Exception:
                            st["errors"] += len(arrs)
                            rows.clear()
                            arrs.clear()
                    st["current"] = res[1][0]
                elif res[0] == "small":
                    st["skipped"] += 1
                    pend.append(res[1])  # نحفظها كمتروكة حتى ما نعيد فحصها كل مرة
                else:
                    st["errors"] += 1
                st["done"] += 1
                if time.time() - last > 0.25:
                    el = time.time() - t0
                    st["rate"] = st["done"] / max(el, 1e-3)
                    self.on_progress(dict(st))
                    last = time.time()
            try:
                flush()
            except Exception:
                pass
            self.db.upsert_many(pend)
        st["phase"] = "stopped" if self.stop_ev.is_set() else "done"
        st["elapsed"] = time.time() - t0
        self.on_progress(dict(st))
