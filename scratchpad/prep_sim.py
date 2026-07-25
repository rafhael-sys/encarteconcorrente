"""Prepara lotes de pares de similaridade para avaliação por visão."""
import json
import os

d = json.load(open("data/similaridade_candidatos.json", encoding="utf-8"))
inc = json.load(open("data/similaridade_incertos.json", encoding="utf-8"))
todo = [p for p in d if p["k"] not in inc]
print("total", len(d), "| ja incertos", len(d) - len(todo), "| a avaliar", len(todo))

missing = 0
for p in todo:
    for f in ("foto_a", "foto_b"):
        if not os.path.exists(p[f]["imagem"]):
            missing += 1
print("imagens faltando:", missing)

B = 13
for i in range(0, len(todo), B):
    batch = todo[i:i + B]
    out = [{"k": p["k"], "a": p["a"], "b": p["b"],
            "foto_a": p["foto_a"], "foto_b": p["foto_b"]} for p in batch]
    json.dump(out, open(f"scratchpad/simbatch_{i // B}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("batch", i // B, len(batch))
