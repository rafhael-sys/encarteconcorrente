#!/usr/bin/env python3
import json
json.dump([], open("data/similaridade_candidatos.json", "w", encoding="utf-8"))
json.dump([], open("data/fila_novos.json", "w", encoding="utf-8"))
print("candidatos de similaridade zerados; fila_novos esvaziada")
