"""Agrega vereditos dos subagentes de similaridade (janela 2026-08-05).

- Lê data/_simverd/verd_*.json (cada = lista de {k,a,b,veredito,motivo}).
- Confere cobertura dos 65 candidatos (todos, uma vez).
- mesmo/diferente -> data/validacoes_inbox/auto_2026-08-05.json
- incerto        -> data/similaridade_incertos.json (k -> "2026-08-05")
- Checa conflito direto de 'mesmo' com regras DIFERENTES existentes.
NÃO grava se houver par faltando/duplicado ou veredito inválido: aborta.
"""
import json
import os
import re
import sys
import unicodedata

HOJE = "2026-08-05"


def nrm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


cand = json.load(open("data/similaridade_candidatos.json", encoding="utf-8"))
cand_by_k = {c["k"]: c for c in cand}
all_k = set(cand_by_k)

verd = {}
dup = []
for fn in sorted(os.listdir("data/_simverd")):
    if not re.match(r"verd_\d+\.json$", fn):
        continue
    arr = json.load(open(os.path.join("data/_simverd", fn), encoding="utf-8"))
    for v in arr:
        k = v["k"]
        if k in verd:
            dup.append(k)
        verd[k] = v

missing = all_k - set(verd)
extra = set(verd) - all_k
bad = [k for k, v in verd.items() if v.get("veredito") not in
       ("mesmo", "diferente", "incerto")]

print(f"candidatos: {len(all_k)} | vereditos: {len(verd)}")
print(f"faltando: {len(missing)} | duplicados: {len(dup)} | extras: {len(extra)} "
      f"| inválidos: {len(bad)}")
if missing:
    print("  FALTANDO:", *sorted(missing), sep="\n   - ")
if dup:
    print("  DUPLICADOS:", *sorted(set(dup)), sep="\n   - ")
if extra:
    print("  EXTRAS:", *sorted(extra), sep="\n   - ")
if bad:
    print("  INVÁLIDOS:", *bad, sep="\n   - ")
if missing or dup or extra or bad:
    print("\nABORTADO: corrija antes de gravar.")
    sys.exit(1)

# regras DIFERENTES existentes (conflito direto com 'mesmo')
diferentes = set()
rp = "data/regras_similaridade.md"
if os.path.exists(rp):
    for line in open(rp, encoding="utf-8"):
        if line.startswith("- DIFERENTES:"):
            mm = re.findall(r"«([^»]*)»", line)
            if len(mm) == 2:
                diferentes.add(frozenset((nrm(mm[0]), nrm(mm[1]))))

conflitos = []
validacoes = []
incertos_novos = {}
cont = {"mesmo": 0, "diferente": 0, "incerto": 0}
for k, v in verd.items():
    ver = v["veredito"]
    cont[ver] += 1
    a, b = cand_by_k[k]["a"], cand_by_k[k]["b"]
    if ver == "incerto":
        incertos_novos[k] = HOJE
        continue
    if ver == "mesmo" and frozenset((nrm(a), nrm(b))) in diferentes:
        conflitos.append(k)
        incertos_novos[k] = HOJE  # em conflito -> trata como incerto (seguro)
        continue
    validacoes.append({"a": a, "b": b, "veredito": ver})

print(f"\nmesmo={cont['mesmo']} diferente={cont['diferente']} "
      f"incerto={cont['incerto']}")
if conflitos:
    print(f"CONFLITO com DIFERENTES (movidos p/ incerto): {len(conflitos)}")
    for k in conflitos:
        print("   -", k)

if len(sys.argv) > 1 and sys.argv[1] == "commit":
    os.makedirs("data/validacoes_inbox", exist_ok=True)
    json.dump({"validacoes": validacoes},
              open(f"data/validacoes_inbox/auto_{HOJE}.json", "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)
    inc = json.load(open("data/similaridade_incertos.json", encoding="utf-8")) \
        if os.path.exists("data/similaridade_incertos.json") else {}
    inc.update(incertos_novos)
    json.dump(inc, open("data/similaridade_incertos.json", "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nGRAVADO: validacoes_inbox/auto_{HOJE}.json "
          f"({len(validacoes)} validações), incertos +{len(incertos_novos)} "
          f"(total {len(inc)})")
else:
    print("\n(dry-run: rode com 'commit' p/ gravar)")
