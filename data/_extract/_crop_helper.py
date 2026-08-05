import json, os
from PIL import Image

base = "/Users/teste/encarteconcorrente/"
out = os.path.join(base, "data/_extract/_crops")
os.makedirs(out, exist_ok=True)
pairs = json.load(open(os.path.join(base, "data/_extract/simpar_5.json")))

def crop(idx, side, foto):
    img = Image.open(os.path.join(base, foto["imagem"])).convert("RGB")
    W, H = img.size
    r = foto["regiao_pct"]
    x = r["x"]/100*W; y = r["y"]/100*H; w = r["w"]/100*W; h = r["h"]/100*H
    # pad 20%
    px = w*0.25; py = h*0.25
    l = max(0, x-px); t = max(0, y-py)
    rr = min(W, x+w+px); bb = min(H, y+h+py)
    c = img.crop((int(l), int(t), int(rr), int(bb)))
    # upscale so smallest side >= 400
    cw, ch = c.size
    scale = max(1.0, 400/min(cw, ch))
    if scale > 1:
        c = c.resize((int(cw*scale), int(ch*scale)))
    p = os.path.join(out, f"p{idx}_{side}.png")
    c.save(p)
    return p

for i, pr in enumerate(pairs):
    crop(i, "a", pr["foto_a"])
    crop(i, "b", pr["foto_b"])
print("done", len(pairs))
