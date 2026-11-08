"""محرك الذكاء الاصطناعي: يحوّل الصور والنصوص إلى بصمات (embeddings) بنفس الفضاء."""
import json
import os
import re

import numpy as np
from PIL import Image, ImageOps

from .paths import models_dir

Image.MAX_IMAGE_PIXELS = 300_000_000

try:
    import pillow_heif  # noqa
    pillow_heif.register_heif_opener()
except Exception:
    pass


def open_image(path, max_side=None):
    im = Image.open(path)
    try:
        im.draft("RGB", (448, 448))  # تسريع JPEG الكبيرة
    except Exception:
        pass
    im = ImageOps.exif_transpose(im)
    if getattr(im, "is_animated", False):
        im.seek(0)
    im = im.convert("RGB")
    if max_side and max(im.size) > max_side:
        im.thumbnail((max_side, max_side))
    return im


class Engine:
    dim = 512

    def __init__(self, use_gpu=True):
        import onnxruntime as ort
        d = models_dir()
        with open(os.path.join(d, "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        self.mean = np.array(cfg["mean"], np.float32).reshape(1, 3, 1, 1)
        self.std = np.array(cfg["std"], np.float32).reshape(1, 3, 1, 1)
        self.max_len = cfg.get("max_len", 128)

        avail = ort.get_available_providers()
        providers = ["CPUExecutionProvider"]
        if use_gpu:
            for p in ("CUDAExecutionProvider", "DmlExecutionProvider"):
                if p in avail:
                    providers = [p, "CPUExecutionProvider"]
                    break
        so = ort.SessionOptions()
        so.log_severity_level = 3
        try:
            self.img = ort.InferenceSession(os.path.join(d, "image.onnx"), so, providers=providers)
        except Exception:
            providers = ["CPUExecutionProvider"]
            self.img = ort.InferenceSession(os.path.join(d, "image.onnx"), so, providers=providers)
        self.device = "GPU" if providers[0] != "CPUExecutionProvider" else "CPU"
        self.txt = ort.InferenceSession(os.path.join(d, "text.onnx"), so,
                                        providers=["CPUExecutionProvider"])
        from tokenizers import Tokenizer
        self.tok = Tokenizer.from_file(os.path.join(d, "tokenizer.json"))
        self.tok.enable_truncation(self.max_len)

    # ------------------------------------------------------------ images
    @staticmethod
    def preprocess(im):
        w, h = im.size
        s = 224 / min(w, h)
        im = im.resize((max(224, round(w * s)), max(224, round(h * s))), Image.BICUBIC)
        w, h = im.size
        l, t = (w - 224) // 2, (h - 224) // 2
        im = im.crop((l, t, l + 224, t + 224))
        return np.asarray(im, np.float32).transpose(2, 0, 1) / 255.0

    def embed_arrays(self, arrs):
        x = (np.stack(arrs) - self.mean) / self.std
        v = self.img.run(None, {"pixel_values": x.astype(np.float32)})[0]
        return _norm(v)

    def embed_image(self, im):
        return self.embed_arrays([self.preprocess(im)])[0]

    # ------------------------------------------------------------ text
    def _embed_texts(self, texts):
        enc = self.tok.encode_batch(texts)
        L = max(len(e.ids) for e in enc)
        ids = np.zeros((len(texts), L), np.int64)
        am = np.zeros((len(texts), L), np.int64)
        for i, e in enumerate(enc):
            ids[i, :len(e.ids)] = e.ids
            am[i, :len(e.ids)] = 1
        return _norm(self.txt.run(None, {"input_ids": ids, "attention_mask": am})[0])

    def embed_text(self, q):
        q = q.strip()
        variants = [q]
        if len(q.split()) <= 3 and not re.match(r"^(صور|photo|picture|image)", q, re.I):
            variants.append(("صورة " if re.search(r"[؀-ۿ]", q) else "a photo of ") + q)
        v = self._embed_texts(variants).mean(0)
        return v / (np.linalg.norm(v) + 1e-9)


class FakeEngine:
    """محرك تجريبي للاختبار بدون نماذج (IBRALENS_FAKE=1)."""
    dim = 512
    device = "CPU (تجريبي)"

    def __init__(self, use_gpu=True):
        rng = np.random.default_rng(0)
        self.P = rng.standard_normal((48, 512)).astype(np.float32)

    @staticmethod
    def preprocess(im):
        return np.asarray(im.resize((32, 32)), np.float32) / 255.0

    def embed_arrays(self, arrs):
        out = []
        for a in arrs:
            h = np.concatenate([np.histogram(a[..., c], 16, (0, 1))[0] for c in range(3)]).astype(np.float32)
            out.append(h @ self.P)
        return _norm(np.array(out))

    def embed_image(self, im):
        return self.embed_arrays([self.preprocess(im)])[0]

    def embed_text(self, q):
        rng = np.random.default_rng(abs(hash(q)) % 2**32)
        v = rng.standard_normal(512).astype(np.float32)
        return v / np.linalg.norm(v)


def _norm(v):
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)


def create_engine(use_gpu=True):
    if os.environ.get("IBRALENS_FAKE") == "1":
        return FakeEngine()
    return Engine(use_gpu)


def models_present():
    if os.environ.get("IBRALENS_FAKE") == "1":
        return True
    d = models_dir()
    return all(os.path.exists(os.path.join(d, f)) for f in
               ("image.onnx", "text.onnx", "tokenizer.json", "config.json"))
