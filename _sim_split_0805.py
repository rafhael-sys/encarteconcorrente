"""Divide os candidatos de similaridade em lotes p/ subagentes."""
import json
import math
import os

cand = json.load(open("data/similaridade_candidatos.json", encoding="utf-8"))
N = 8
size = math.ceil(len(cand) / N)
os.makedirs("data/_simlote", exist_ok=True)
for i in range(N):
    chunk = cand[i * size:(i + 1) * size]
    if not chunk:
        continue
    slim = []
    for c in chunk:
        slim.append({
            "k": c["k"],
            "a": c["a"],
            "b": c["b"],
            "foto_a": c["foto_a"],
            "foto_b": c["foto_b"],
        })
    fn = f"data/_simlote/lote_{i + 1}.json"
    json.dump(slim, open(fn, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{fn}: {len(slim)} pares")
