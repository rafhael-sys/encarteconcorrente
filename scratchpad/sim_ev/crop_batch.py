import json, os
from PIL import Image

base = "/Users/teste/encarteconcorrente"
batch = json.load(open(os.path.join(base, "scratchpad/sim_ev/batch_1.json")))
outdir = os.path.join(base, "scratchpad/sim_ev/crops")
os.makedirs(outdir, exist_ok=True)

def crop(idx, side, foto):
    path = os.path.join(base, foto["imagem"])
    if not os.path.exists(path):
        print(f"MISSING {idx}{side}: {path}")
        return
    im = Image.open(path).convert("RGB")
    W, H = im.size
    r = foto["regiao_pct"]
    x = r["x"]/100*W; y = r["y"]/100*H; w = r["w"]/100*W; h = r["h"]/100*H
    px = max(w*0.4, 40); py = max(h*0.4, 40)
    l = max(0, int(x-px)); t = max(0, int(y-py))
    rr = min(W, int(x+w+px)); bb = min(H, int(y+h+py))
    cr = im.crop((l, t, rr, bb))
    cw, ch = cr.size
    if max(cw, ch) < 700:
        scale = min(3, 700/max(cw, ch))
        cr = cr.resize((int(cw*scale), int(ch*scale)))
    out = os.path.join(outdir, f"p{idx}_{side}.jpg")
    cr.save(out, quality=90)
    print(f"p{idx}_{side}: {os.path.basename(path)} {W}x{H} -> {cr.size}")

for i, pair in enumerate(batch, 1):
    crop(i, "a", pair["foto_a"])
    crop(i, "b", pair["foto_b"])
print("done")
