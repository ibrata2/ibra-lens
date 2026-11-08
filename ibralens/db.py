"""قاعدة بيانات الفهرس (SQLite) + مصفوفة البصمات بالذاكرة للبحث السريع."""
import os
import sqlite3
import threading

import numpy as np

from .paths import data_dir

SCHEMA = """
CREATE TABLE IF NOT EXISTS images(
  id INTEGER PRIMARY KEY,
  path TEXT UNIQUE NOT NULL,
  size INTEGER, mtime REAL,
  width INTEGER, height INTEGER,
  fhash TEXT, phash INTEGER,
  emb BLOB
);
CREATE INDEX IF NOT EXISTS ix_fhash ON images(fhash);
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
"""


class DB:
    def __init__(self, path=None):
        self.path = path or os.path.join(data_dir(), "index.db")
        self.lock = threading.RLock()
        self.con = sqlite3.connect(self.path, check_same_thread=False)
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.execute("PRAGMA synchronous=NORMAL")
        self.con.executescript(SCHEMA)
        self.con.commit()
        self._mat = None
        self._ids = None
        self._paths = None
        self.dirty = True

    # ------------------------------------------------------------ write
    def known(self):
        with self.lock:
            return {p: (s, m) for p, s, m in self.con.execute("SELECT path,size,mtime FROM images")}

    def upsert_many(self, rows):
        """rows: (path,size,mtime,w,h,fhash,phash,emb_float16_bytes)"""
        if not rows:
            return
        with self.lock:
            self.con.executemany(
                "INSERT INTO images(path,size,mtime,width,height,fhash,phash,emb) VALUES(?,?,?,?,?,?,?,?) "
                "ON CONFLICT(path) DO UPDATE SET size=excluded.size,mtime=excluded.mtime,width=excluded.width,"
                "height=excluded.height,fhash=excluded.fhash,phash=excluded.phash,emb=excluded.emb", rows)
            self.con.commit()
            self.dirty = True

    def remove_paths(self, paths):
        if not paths:
            return
        with self.lock:
            self.con.executemany("DELETE FROM images WHERE path=?", [(p,) for p in paths])
            self.con.commit()
            self.dirty = True

    def clear(self):
        with self.lock:
            self.con.execute("DELETE FROM images")
            self.con.commit()
            self.con.execute("VACUUM")
            self.dirty = True

    def count(self):
        with self.lock:
            return self.con.execute("SELECT COUNT(*) FROM images WHERE emb IS NOT NULL").fetchone()[0]

    def total_size(self):
        with self.lock:
            return self.con.execute("SELECT COALESCE(SUM(size),0) FROM images WHERE emb IS NOT NULL").fetchone()[0]

    def info(self, ids):
        with self.lock:
            out = {}
            for i in range(0, len(ids), 500):
                chunk = [int(x) for x in ids[i:i + 500]]
                q = "SELECT id,path,size,width,height,mtime FROM images WHERE id IN (%s)" % ",".join("?" * len(chunk))
                for r in self.con.execute(q, chunk):
                    out[r[0]] = {"id": r[0], "path": r[1], "size": r[2], "w": r[3], "h": r[4], "mtime": r[5]}
            return out

    def hashes(self):
        with self.lock:
            return self.con.execute("SELECT id,fhash,phash,size FROM images WHERE emb IS NOT NULL").fetchall()

    # ------------------------------------------------------------ search
    def _load(self):
        with self.lock:
            rows = self.con.execute("SELECT id,emb FROM images WHERE emb IS NOT NULL").fetchall()
        if rows:
            self._ids = np.array([r[0] for r in rows], np.int64)
            self._mat = np.frombuffer(b"".join(r[1] for r in rows), np.float16).reshape(len(rows), -1).astype(np.float32)
        else:
            self._ids = np.zeros(0, np.int64)
            self._mat = np.zeros((0, 512), np.float32)
        self.dirty = False

    def search(self, vec, top=300, exclude_path=None):
        if self.dirty or self._mat is None:
            self._load()
        if len(self._ids) == 0:
            return []
        s = self._mat @ vec.astype(np.float32)
        k = min(top, len(s))
        idx = np.argpartition(-s, k - 1)[:k]
        idx = idx[np.argsort(-s[idx])]
        res = [(int(self._ids[i]), float(s[i])) for i in idx]
        info = self.info([r[0] for r in res])
        out = []
        for i, sc in res:
            d = info.get(i)
            if d and d["path"] != exclude_path:
                d["score"] = sc
                out.append(d)
        return out
