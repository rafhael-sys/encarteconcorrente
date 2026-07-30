import json, os, unicodedata
def nrm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())
def chave_par(a, b):
    return ' || '.join(sorted([nrm(a), nrm(b)]))

dec = {}
if os.path.exists('data/similaridade_decisoes.json'):
    dec = json.load(open('data/similaridade_decisoes.json'))
print('decisões humanas/prévias existentes:', len(dec))

inbox = json.load(open('data/validacoes_inbox/auto_2026-07-29.json'))['validacoes']
conflitos = []
iguais = []
novos = 0
for v in inbox:
    k = chave_par(v['a'], v['b'])
    if k in dec:
        if dec[k]['veredito'] != v['veredito']:
            conflitos.append((v['a'], v['b'], dec[k]['veredito'], v['veredito']))
        else:
            iguais.append(k)
    else:
        novos += 1
print('inbox:', len(inbox), '| novos:', novos, '| já decididos iguais:', len(iguais), '| CONFLITOS:', len(conflitos))
for c in conflitos:
    print('  !! CONFLITO: «%s» || «%s» — humano=%s, auto=%s' % c)
