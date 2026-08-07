import json, os, glob

edir = 'data/_extract'
files = sorted(glob.glob(os.path.join(edir, 'w0807_*.json')))
print('arquivos w0807:', len(files))
for fp in files:
    try:
        d = json.load(open(fp))
    except Exception as e:
        print('  ERRO', os.path.basename(fp), e)
        continue
    if not isinstance(d, dict) or 'pages' not in d:
        print('  FORMATO?', os.path.basename(fp))
        continue
    pages = d.get('pages') or {}
    nprod = sum(len(v) for v in pages.values())
    npg = sum(1 for v in pages.values() if v)
    print(f"  {os.path.basename(fp):58s} sc={d.get('shortcode')} disc={d.get('discard')} {d.get('inicio')}..{d.get('fim')} pgs={len(pages)} comprod={npg} nprod={nprod}")
