import json, os, glob
edir = 'data/_extract'
files = sorted(glob.glob(os.path.join(edir, 'w0806b_*.json')))
print("=== w0806b extract files: pages/products per file ===")
grand = 0
for f in files:
    if f.endswith('w0806b_meta.json'):
        continue
    d = json.load(open(f))
    npg = len(d)
    nprod = sum(len(v) for v in d.values())
    grand += nprod
    sc = os.path.basename(f)[len('w0806b_'):-5]
    print("%-48s pages=%2d prod=%3d" % (sc, npg, nprod))
print("GRAND TOTAL products:", grand)
print()
print("=== Mar Vermelho STORY frames (pagekeys) ===")
d = json.load(open(os.path.join(edir, 'w0806b_story_marvermelhoatacado_20260806.json')))
for k in d:
    print("  %s  -> %d prod  | first: %s" % (k, len(d[k]), d[k][0]['n'][:50] if d[k] else ''))
