# -*- coding: utf-8 -*-
import json, os, unicodedata

def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())

def chave_par(a, b):
    return ' || '.join(sorted([nrm(a), nrm(b)]))

# veredito por chave k (formato dos candidatos)
V = {
 # batch 0-13 (todos mesmo)
 "rodo multilar 30 cm sem cabo unid || rodo multilar 30cm sem cabo unid": "mesmo",
 "lava roupas liquido limpa mil 3l || lava roupas liquido limpamil 3l": "mesmo",
 "vinho chileno pictor 750ml cabernet sauvignon tinto sc || vinho chileno pictor 750ml cabernet sauvignon tto sc": "mesmo",
 "bebida proteica italac s/ lactose 15g 250ml (sabores) || bebida proteica italac sem lactose 15g 250ml sabores": "mesmo",
 "absorvente sempre livre adapt 8 abas c/8 suave || absorvente sempre livre adapt s/ abas c/8 suave": "mesmo",
 "toalha umedecida piquitucho hidrata c/140 || toalha umedecida piquitucho hidrate c/140": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua kg || coxa com sobrecoxa dorsal jagua kg": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua || coxa com sobrecoxa dorsal jagua": "mesmo",
 "sapolio radium cremoso 250ml classico ou cloro || sapolio radium cremoso fr 250ml classico ou cloro": "mesmo",
 "lava roupa liquido limpamil 3l || lava roupas liquido limpa mil 3l": "mesmo",
 "creme de tratamento elseve 300g colageno lifter || creme tratamento elseve 300g colageno lifter": "mesmo",
 "amaciante de roupa comfort l500 p400ml original || amaciante roupa comfort l500 p400ml original": "mesmo",
 "cafe sao braz familia 250g (almofada ou a vacuo) || cafe sao braz familia 250g (almofada/a vacuo)": "mesmo",
 # batch 13-26 (todos mesmo)
 "creme tratamento elseve 300g colag lifter || creme tratamento elseve 300g colageno lifter": "mesmo",
 "papel higienico caprice folha dupla 20m leve 12 pague 11 || papel higienico caprice folha dupla leve 12 pague 11": "mesmo",
 "file de peito bom todo 1kg iqf ou bandeja || file peito bom todo 1kg iqf ou bandeja": "mesmo",
 "linguica suina para churrasco aurora || linguica suina para churrasco aurora kg": "mesmo",
 "costela suina em tiras lar congelada || costela suina em tiras lar congelada kg": "mesmo",
 "leite em po confianca integral 200g || leite em po confianca integral sc 200g": "mesmo",
 "lava roupas liquido omo varios tipos bombona 5l || lava roupas liquido omo varios tipos bombona com 5l": "mesmo",
 "cerv petra ultra 275ml ln s/gluten || cerveja petra ultra 275ml ln s/ gluten": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua || coxa com sobrecoxa c/dorsal jagua kg": "mesmo",
 "file mignon suino lar congelado || file mignon suino lar congelado kg": "mesmo",
 "matambrito suino lar congelado || matambrito suino lar congelado kg": "mesmo",
 "file de peito bom todo 1kg iqf ou bandeja || file peito bomtodo 1kg iqf ou bandeja": "mesmo",
 "xicara cha alleanza c/ pires || xicara de cha alleanza c/ pires": "mesmo",
 # batch 26-39
 "galinha pequena qdelicia || galinha pequena qdelicia kg": "mesmo",
 "biscoito cookies bauducco 100g original ou cookies bauducco max 96g dentadura || biscoito cookies bauducco 100g original ou cookies max 96g dentadura": "mesmo",
 "pastilha ades pro pato 3un 20% desc floral ou citrus || pastilha adesiva pro pato 3un 20% desconto floral ou citrus": "mesmo",
 "cupim bovino (congelado) || cupim bovino congelado kg": "mesmo",
 "bisc cookies bauduco 100g original ou bisc cookies bauducco max 96g dentadura || biscoito cookies bauducco 100g original ou cookies bauducco max 96g dentadura": "mesmo",
 "galinha grande somave || galinha grande somave kg": "mesmo",
 "filezinho de peito de frango (sassami) sadia congelado bdj 1kg || filezinho de peito de frango sadia congelado bdj 1kg": "mesmo",
 "whisky white horse 1 litro || whisky white horse gfa 1 litro": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua || coxa com sobrecoxa dorsal jagua kg": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua kg || coxa com sobrecoxa dorsal jagua": "mesmo",
 "file de peito de frango lar 1kg || file de peito de frango levo 1kg": "diferente",
 "carvao vegetal jucurutu pct 3kg || carvao vegetal jucurutu saco 3kg": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua || coxa com sobrecoxa c/dorsal kg": "incerto",
 # batch 39-52
 "file de peito de frango bom todo 1kg (congelado) || file de peito de frango bom todo 1kg congelado bandeja": "mesmo",
 "manteiga itacolomy com sal pt 500g || manteiga itacolomy comum com sal pt 500g": "mesmo",
 "absorvente sempre livre adapt c/8 suave || absorvente sempre livre adapt s/ abas c/8 suave": "mesmo",
 "aperitivo aperol 750ml || aperitivo aperol gfa 750ml": "mesmo",
 "coxa com sobrecoxa de frango congelada || coxa com sobrecoxa de frango friato congelada": "incerto",
 "linguica calabresa imperio kg || linguica calabresa perdigao kg": "diferente",
 "lavanda johnson's baby infantil 200ml || lavanda johnsons baby inf 200ml": "mesmo",
 "papel higienico deluxe 20m leve 12 pague 11 || papel higienico deluxe 20m lv12 pg11": "mesmo",
 "coxa com sobrecoxa c/dorsal jagua kg || coxa com sobrecoxa c/dorsal kg": "incerto",
 "coxa com sobrecoxa de frango congelada || coxa com sobrecoxa de frango envelopada": "mesmo",
 "linguica toscana aurora 700g ou pernil aurora 700g ou frango aurora 700g || linguica toscana aurora 700g ou pernil ou frango aurora 700g": "mesmo",
 "ling toscana aurora 700g ou ling pernil aurora 700g ou ling frango aurora 700g || linguica toscana aurora 700g ou pernil aurora 700g ou frango aurora 700g": "mesmo",
 "file de peito bom todo 1kg bandeja || file de peito bom todo 1kg iqf ou bandeja": "mesmo",
 # batch 52-65
 "amaciante de roupas comfort 1,5l fragrancias || amaciante de roupas sonho 1,5l fragrancias": "diferente",
 "coxa com sobrecoxa de frango congelada || coxa com sobrecoxa de frango copacol congelada": "diferente",
 "papel higienico caprice folha dupla leve 12 pague 11 || papel higienico caprice neutro 20m folha dupla leve 12 pague 11": "mesmo",
 "papel higienico caprice folha dupla 20m leve 12 pague 11 (neutro) || papel higienico caprice folha dupla leve 12 pague 11": "mesmo",
 "galinha pequena q'delicia cong kg || galinha pequena qdelicia kg": "mesmo",
 "cafe sao braz 250g almofada/a vacuo || cafe sao braz familia 250g (almofada/a vacuo)": "mesmo",
 "morangos congelados 1,02kg || morangos congelados canaa 1,02kg": "incerto",
 "linguica suina para churrasco aurora kg || linguica suina para churrasco suinco kg": "diferente",
 "queijo mussarela dombla peca ou pedaco kg || queijo mussarela domilac pc ou pdc kg": "diferente",
 "papel higienico floral folha dupla 20 metros pct c/12 || papel higienico floral folha dupla 20m c/12": "mesmo",
 "achocolatado em po italac 200g || achocolatado em po italac chocky 200g": "mesmo",
 "file mignon suino lar congelado kg || file-mignon suino seara congelado": "diferente",
 "coxa com sobrecoxa de frango congelada || coxa com sobrecoxa de frango mauricea congelada": "diferente",
}

cand = json.load(open('data/similaridade_candidatos.json'))
decis = {}
if os.path.exists('data/similaridade_decisoes.json'):
    try:
        decis = json.load(open('data/similaridade_decisoes.json'))
    except Exception:
        decis = {}

validacoes = []       # mesmo/diferente -> auto file
incertos_novos = {}   # k -> data
faltando = []
conflitos = []
counts = {"mesmo": 0, "diferente": 0, "incerto": 0}

for item in cand:
    k = item['k']
    a = item['a']
    b = item['b']
    ver = V.get(k)
    if ver is None:
        faltando.append(k)
        # fallback seguro: incerto
        incertos_novos[k] = "2026-08-04"
        continue
    counts[ver] += 1
    if ver == 'incerto':
        incertos_novos[k] = "2026-08-04"
        continue
    # conflito com decisao humana existente?
    ck = chave_par(a, b)
    prev = decis.get(ck)
    if prev and prev.get('veredito') in ('mesmo', 'diferente') and prev['veredito'] != ver:
        conflitos.append((k, prev['veredito'], ver))
        continue  # prioridade da validacao humana
    validacoes.append({"a": a, "b": b, "veredito": ver})

print("counts:", counts)
print("faltando (sem verdict no mapa):", faltando)
print("conflitos com decisao humana (pulados):", conflitos)
print("validacoes p/ auto file:", len(validacoes))
print("incertos novos:", len(incertos_novos))

# --- grava auto file ---
os.makedirs('data/validacoes_inbox', exist_ok=True)
tmp = 'data/validacoes_inbox/auto_2026-08-04.json.tmp'
json.dump({"validacoes": validacoes}, open(tmp, 'w'), ensure_ascii=False, indent=1)
os.replace(tmp, 'data/validacoes_inbox/auto_2026-08-04.json')

# --- merge incertos ---
inc = {}
if os.path.exists('data/similaridade_incertos.json'):
    try:
        inc = json.load(open('data/similaridade_incertos.json'))
    except Exception:
        inc = {}
antes = len(inc)
for k, d in incertos_novos.items():
    inc.setdefault(k, d)
tmp = 'data/similaridade_incertos.json.tmp'
json.dump(inc, open(tmp, 'w'), ensure_ascii=False, indent=1)
os.replace(tmp, 'data/similaridade_incertos.json')
print("incertos.json: %d -> %d" % (antes, len(inc)))
