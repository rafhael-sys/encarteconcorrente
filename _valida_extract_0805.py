"""Valida integridade das extrações w0805 antes do commit."""
import json
import os
import re

base = "data/_extract"
price_re = re.compile(r"^\d{1,3}(\.\d{3})*,\d{2}$|^\d+,\d{2}$")
problems = 0
total = 0
for fn in sorted(os.listdir(base)):
    if not fn.startswith("w0805_"):
        continue
    d = json.load(open(os.path.join(base, fn), encoding="utf-8"))
    for pk, items in d.items():
        for i, it in enumerate(items):
            total += 1
            miss = [k for k in ("n", "p", "u", "x", "y", "w", "h") if k not in it]
            if miss:
                print(f"  [{fn}:{pk}#{i}] faltam campos {miss}: {it}")
                problems += 1
                continue
            if not price_re.match(str(it["p"])):
                print(f"  [{fn}:{pk}#{i}] preço suspeito '{it['p']}' ({it['n']})")
                problems += 1
            for k in ("x", "y", "w", "h"):
                v = it[k]
                if not isinstance(v, (int, float)) or v < 0 or v > 100:
                    print(f"  [{fn}:{pk}#{i}] {k}={v} fora de 0-100 ({it['n']})")
                    problems += 1
print(f"\nTotal itens: {total} | problemas: {problems}")
