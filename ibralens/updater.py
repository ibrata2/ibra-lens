"""فحص التحديثات من GitHub Releases وتنصيب الإصدار الجديد فوق القديم."""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

from .paths import REPO, VERSION

API = f"https://api.github.com/repos/{REPO}/releases/latest"


def _ver(t):
    t = t.lstrip("vV")
    out = []
    for p in t.split("."):
        n = "".join(ch for ch in p if ch.isdigit())
        out.append(int(n or 0))
    return tuple(out + [0] * (3 - len(out)))


def check():
    """يرجع (tag, url, size, notes) إذا أكو إصدار أحدث، وإلا None."""
    req = urllib.request.Request(API, headers={"User-Agent": "IBRA-LENS", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.load(r)
    tag = data.get("tag_name", "")
    if _ver(tag) <= _ver(VERSION):
        return None
    for a in data.get("assets", []):
        if a["name"].lower().endswith("setup.exe"):
            return tag, a["browser_download_url"], a.get("size", 0), data.get("body", "")
    return None


def download(url, size, progress=None):
    path = os.path.join(tempfile.gettempdir(), "IBRA-LENS-Setup.exe")
    req = urllib.request.Request(url, headers={"User-Agent": "IBRA-LENS"})
    with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
        got = 0
        while True:
            b = r.read(1 << 18)
            if not b:
                break
            f.write(b)
            got += len(b)
            if progress and size:
                progress(int(got * 100 / size))
    return path


def install(path):
    subprocess.Popen([path, "/SILENT", "/CLOSEAPPLICATIONS", "/NORESTART"], close_fds=True)
    sys.exit(0)
