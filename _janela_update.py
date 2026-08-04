import json, shutil, datetime, os
stamp = datetime.date.today().strftime('%Y%m%d')

acts = json.load(open('data/actions.json'))
prods = json.load(open('data/products.json'))
canon = json.load(open('data/canon.json'))

# --- 1. Rede Mais story action (única ação nova da janela) ---
rm_pages = [
 "story_redemaisrn_3956192830595339411.jpg", "story_redemaisrn_3956192981070020281.jpg",
 "story_redemaisrn_3956193148641033394.jpg", "story_redemaisrn_3956193382355871148.jpg",
 "story_redemaisrn_3956193457702547147.jpg", "story_redemaisrn_3956193653114931249.jpg",
 "story_redemaisrn_3956193761193993331.jpg", "story_redemaisrn_3956193951975908085.jpg",
 "story_redemaisrn_3956194063250979325.jpg", "story_redemaisrn_3956194276136910294.jpg",
 "story_redemaisrn_3956194358085387848.jpg",
]
new_action = {
 "id": "story_redemaisrn_20260804", "perfil": "redemaisrn",
 "titulo": "Rede Mais — Aniversário 26 anos (story)", "banner": "Rede Mais",
 "segmento": "propria", "inicio": "2026-08-01", "fim": "2026-08-10", "carrossel": True,
 "shortcode": "story_redemaisrn_20260804", "caption": "",
 "paginas": rm_pages, "adicionado_em": "2026-08-04", "fonte": "story", "link": "",
}
assert not any(a['id'] == 'story_redemaisrn_20260804' for a in acts), "id ja existe"
acts.append(new_action)

# --- 2. produtos por frame ---
prod_map = {
 "story_redemaisrn_3956193951975908085": [{"n": "Sabonete Líquido Skalinha Bebê Lavanda 200ml", "p": "7,99", "u": "cada", "x": 28, "y": 35, "w": 44, "h": 42}],
 "story_redemaisrn_3956194063250979325": [{"n": "Açúcar Triturado Ecoçúcar Extra Fino 1kg", "p": "2,69", "u": "cada", "x": 28, "y": 42, "w": 54, "h": 34}],
}
for pg in rm_pages:
    k = pg[:-4]
    prods[k] = prod_map.get(k, [])

# --- 3. canon: agrupar com grupos existentes ---
def find_group_by_ref(ref):
    for g in canon:
        if ref in g['m']:
            return g
    return None

g_acucar = find_group_by_ref("DbeZSRWjQOF_p1#3")
g_sabon = find_group_by_ref("DbmHocUjRRD_p1#4")
print("grupo acucar:", g_acucar['n'] if g_acucar else "NAO ACHOU")
print("grupo sabonete:", g_sabon['n'] if g_sabon else "NAO ACHOU")

if g_acucar:
    ref = "story_redemaisrn_3956194063250979325#0"
    if ref not in g_acucar['m']:
        g_acucar['m'].append(ref)
else:
    canon.append({"n": "Acucar Triturado Ecocucar Extra Fino 1kg", "u": "cada", "m": ["story_redemaisrn_3956194063250979325#0"]})
    print("CRIADO grupo novo acucar")

if g_sabon:
    ref = "story_redemaisrn_3956193951975908085#0"
    if ref not in g_sabon['m']:
        g_sabon['m'].append(ref)
else:
    canon.append({"n": "Sabonete Liquido Skalinha Bebe Lavanda 200ml", "u": "cada", "m": ["story_redemaisrn_3956193951975908085#0"]})
    print("CRIADO grupo novo sabonete")

# --- backups + save ---
for f in ['data/actions.json', 'data/products.json', 'data/canon.json']:
    shutil.copy2(f, f + '.bak-' + stamp + '-janela')

def save(path, data):
    tmp = path + '.tmp'
    json.dump(data, open(tmp, 'w'), ensure_ascii=False, indent=1)
    os.replace(tmp, path)

save('data/actions.json', acts)
save('data/products.json', prods)
save('data/canon.json', canon)
print("OK actions=%d products=%d canon=%d" % (len(acts), len(prods), len(canon)))
