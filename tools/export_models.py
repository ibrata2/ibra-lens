"""
تصدير نماذج الذكاء الاصطناعي إلى ONNX (يشتغل داخل GitHub Actions).

- image.onnx : مشفّر الصور CLIP ViT-B/32  (pixel_values -> embedding 512)
- text.onnx  : مشفّر النص متعدد اللغات (عربي/إنكليزي/...) بنفس فضاء CLIP
- tokenizer.json

الاستخدام:  python tools/export_models.py <output_dir>
"""
import os
import sys
import json

import numpy as np
import torch
from transformers import CLIPModel
from sentence_transformers import SentenceTransformer

OUT = sys.argv[1] if len(sys.argv) > 1 else "models"
os.makedirs(OUT, exist_ok=True)
torch.set_grad_enabled(False)


# ---------------------------------------------------------------- image
class ImageEncoder(torch.nn.Module):
    def __init__(self, clip):
        super().__init__()
        self.vision = clip.vision_model
        self.proj = clip.visual_projection

    def forward(self, pixel_values):
        pooled = self.vision(pixel_values=pixel_values).pooler_output
        return self.proj(pooled)


clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", attn_implementation="eager").eval()
img_enc = ImageEncoder(clip).eval()
dummy = torch.randn(2, 3, 224, 224)
img_path = os.path.join(OUT, "image.onnx")
torch.onnx.export(
    img_enc, (dummy,), img_path,
    input_names=["pixel_values"], output_names=["embedding"],
    dynamic_axes={"pixel_values": {0: "batch"}, "embedding": {0: "batch"}},
    opset_version=17, do_constant_folding=True, dynamo=False,
)
print("image.onnx done")


# ---------------------------------------------------------------- text
st = SentenceTransformer("sentence-transformers/clip-ViT-B-32-multilingual-v1", device="cpu",
                         model_kwargs={"attn_implementation": "eager"}).eval()
print(st)


class TextEncoder(torch.nn.Module):
    def __init__(self, st):
        super().__init__()
        self.bert = st[0].auto_model
        self.dense = st[2]

    def forward(self, input_ids, attention_mask):
        tok = self.bert(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        m = attention_mask.unsqueeze(-1).to(tok.dtype)
        pooled = (tok * m).sum(1) / m.sum(1).clamp(min=1e-9)
        return self.dense({"sentence_embedding": pooled})["sentence_embedding"]


txt_enc = TextEncoder(st).eval()
tok = st.tokenizer(["صورة سيارة", "a photo of a tattoo"], padding=True, return_tensors="pt")
txt_path_fp32 = os.path.join(OUT, "text_fp32.onnx")
torch.onnx.export(
    txt_enc, (tok["input_ids"], tok["attention_mask"]), txt_path_fp32,
    input_names=["input_ids", "attention_mask"], output_names=["embedding"],
    dynamic_axes={"input_ids": {0: "batch", 1: "seq"},
                  "attention_mask": {0: "batch", 1: "seq"},
                  "embedding": {0: "batch"}},
    opset_version=17, do_constant_folding=True, dynamo=False,
)

from onnxruntime.quantization import quantize_dynamic, QuantType
txt_path = os.path.join(OUT, "text.onnx")
quantize_dynamic(txt_path_fp32, txt_path, weight_type=QuantType.QInt8, per_channel=True)
os.remove(txt_path_fp32)
for f in os.listdir(OUT):
    if f.endswith(".data"):
        print("WARNING external data:", f)
print("text.onnx done")

# tokenizer
st.tokenizer.backend_tokenizer.save(os.path.join(OUT, "tokenizer.json"))
with open(os.path.join(OUT, "config.json"), "w", encoding="utf-8") as f:
    json.dump({"max_len": 128, "dim": 512,
               "mean": [0.48145466, 0.4578275, 0.40821073],
               "std": [0.26862954, 0.26130258, 0.27577711]}, f)

# ---------------------------------------------------------------- verify
import onnxruntime as ort
from tokenizers import Tokenizer

s_img = ort.InferenceSession(img_path, providers=["CPUExecutionProvider"])
a = s_img.run(None, {"pixel_values": dummy.numpy()})[0]
b = img_enc(dummy).numpy()
print("image max diff:", float(np.abs(a - b).max()))
assert np.abs(a - b).max() < 1e-2

tk = Tokenizer.from_file(os.path.join(OUT, "tokenizer.json"))
s_txt = ort.InferenceSession(txt_path, providers=["CPUExecutionProvider"])


def emb(texts):
    enc = tk.encode_batch(texts)
    L = max(len(e.ids) for e in enc)
    ids = np.zeros((len(texts), L), np.int64)
    am = np.zeros((len(texts), L), np.int64)
    for i, e in enumerate(enc):
        ids[i, :len(e.ids)] = e.ids
        am[i, :len(e.ids)] = 1
    v = s_txt.run(None, {"input_ids": ids, "attention_mask": am})[0]
    return v / np.linalg.norm(v, axis=1, keepdims=True)


ref = st.encode(["صورة سيارة", "a photo of a child"], normalize_embeddings=True)
mine = emb(["صورة سيارة", "a photo of a child"])
print("text cos (onnx int8 vs torch):", (ref * mine).sum(1))
assert (ref * mine).sum(1).min() > 0.97

e = emb(["صورة سيارة", "a photo of a car", "صورة طفل", "a photo of a child", "وشم", "a tattoo"])
sim = e @ e.T
print(np.round(sim, 3))
assert sim[0, 1] > sim[0, 3] and sim[2, 3] > sim[2, 1]
for f in sorted(os.listdir(OUT)):
    print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")
print("ALL OK")
