"""Consolida vereditos de similaridade em inbox + incertos."""
import json

HOJE = "2026-07-24"
verdicts = json.load(open("scratchpad/verdicts.json", encoding="utf-8"))
cand = json.load(open("data/similaridade_candidatos.json", encoding="utf-8"))
by_k = {p["k"]: p for p in cand}


def nomes(k: str) -> tuple:
    """Recupera nomes de exibição a/b do par pelo k (fallback = metades do k)."""
    p = by_k.get(k)
    if p:
        return p["a"], p["b"]
    partes = k.split(" || ")
    return partes[0], partes[-1]


validacoes = []
incertos_novos = {}
for k, ver in verdicts.items():
    a, b = nomes(k)
    if ver in ("mesmo", "diferente"):
        validacoes.append({"a": a, "b": b, "veredito": ver})
    else:
        incertos_novos[k] = HOJE

json.dump({"validacoes": validacoes},
          open("data/validacoes_inbox/auto_2026-07-24.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

inc = json.load(open("data/similaridade_incertos.json", encoding="utf-8"))
inc.update(incertos_novos)
json.dump(inc, open("data/similaridade_incertos.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("validacoes (mesmo/diferente):", len(validacoes))
print("incertos novos:", len(incertos_novos), list(incertos_novos.keys()))
print("total verdicts:", len(verdicts))
