import json, unicodedata

HOJE = "2026-08-06"

# Vereditos na MESMA ORDEM dos pares em cada data/_simlote/lote_N.json
VERD = {
 0: ["mesmo","mesmo","mesmo","mesmo","mesmo","mesmo","mesmo","mesmo","mesmo"],
 1: ["mesmo","diferente","mesmo","mesmo","diferente","mesmo","mesmo","mesmo","diferente"],
 2: ["mesmo","diferente","mesmo","mesmo","mesmo","mesmo","diferente","diferente","mesmo"],
 3: ["mesmo","diferente","diferente","diferente","mesmo","incerto","mesmo","diferente","diferente"],
 4: ["mesmo","diferente","diferente","diferente","diferente","diferente","mesmo","mesmo","mesmo"],
 5: ["mesmo","incerto","diferente","diferente","mesmo","incerto","mesmo","mesmo","diferente"],
 6: ["diferente","diferente","mesmo","mesmo","mesmo","incerto","mesmo","diferente","diferente"],
 7: ["diferente","mesmo"],
}

def nrm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return " ".join("".join(c for c in s if unicodedata.category(c)!="Mn").split())

decisoes = json.load(open("data/similaridade_decisoes.json", encoding="utf-8"))
incertos = json.load(open("data/similaridade_incertos.json", encoding="utf-8"))

def decidido(k, a, b):
    """True se o par ja tem decisao (em qualquer orientacao)."""
    if k in decisoes:
        return decisoes[k]["veredito"]
    kk = nrm(b) + " || " + nrm(a)
    if kk in decisoes:
        return decisoes[kk]["veredito"]
    kk2 = nrm(a) + " || " + nrm(b)
    if kk2 in decisoes:
        return decisoes[kk2]["veredito"]
    return None

inbox = []
add_incertos = {}
conflitos = []
redundantes = 0

for i in range(8):
    lote = json.load(open("data/_simlote/lote_%d.json" % i, encoding="utf-8"))
    vs = VERD[i]
    assert len(lote) == len(vs), "lote %d: %d pares mas %d vereditos" % (i, len(lote), len(vs))
    for par, ver in zip(lote, vs):
        k, a, b = par["k"], par["a"], par["b"]
        ja = decidido(k, a, b)
        if ver == "incerto":
            if ja is None and k not in incertos:
                add_incertos[k] = HOJE
            continue
        # mesmo / diferente
        if ja is not None:
            if ja == ver:
                redundantes += 1
            else:
                conflitos.append((k, "auto=%s" % ver, "existente=%s" % ja))
            continue  # nunca sobrescreve decisao existente
        inbox.append({"a": a, "b": b, "veredito": ver})

print("== RESUMO CONSOLIDACAO ==")
print("inbox (mesmo/diferente novos):", len(inbox))
nm = sum(1 for x in inbox if x["veredito"]=="mesmo")
print("   mesmo:", nm, "| diferente:", len(inbox)-nm)
print("incertos novos:", len(add_incertos))
print("redundantes (ja decididos, mesmo veredito):", redundantes)
print("CONFLITOS (auto x existente) — NAO sobrescritos:")
for c in conflitos: print("   ", c)
print()
for x in inbox:
    print("  %-9s %s || %s" % (x["veredito"], x["a"], x["b"]))
print("\n-- incertos novos --")
for k in add_incertos: print("  ", k)

import sys
if len(sys.argv) > 1 and sys.argv[1] == "commit":
    import os
    os.makedirs("data/validacoes_inbox", exist_ok=True)
    json.dump({"validacoes": inbox},
              open("data/validacoes_inbox/auto_%s.json" % HOJE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    incertos.update(add_incertos)
    json.dump(incertos, open("data/similaridade_incertos.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\nGRAVADO: data/validacoes_inbox/auto_%s.json (%d) + incertos (+%d = %d)" % (
        HOJE, len(inbox), len(add_incertos), len(incertos)))
