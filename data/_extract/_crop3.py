import json, os
from PIL import Image

base = "/Users/teste/encarteconcorrente"
pairs = json.load(open(os.path.join(base, "data/_extract/simpar_3.json")))
outdir = os.path.join(base, "data/_extract/_crops3")
os.makedirs(outdir, exist_ok=True)


def crop(imgpath, reg, outpath, pad=0.15):
    im = Image.open(imgpath).convert("RGB")
    W, H = im.size
    x = reg["x"] / 100.0 * W
    y = reg["y"] / 100.0 * H
    w = reg["w"] / 100.0 * W
    h = reg["h"] / 100.0 * H
    px = w * pad
    py = h * pad
    left = max(0, x - px)
    top = max(0, y - py)
    right = min(W, x + w + px)
    bottom = min(H, y + h + py)
    c = im.crop((int(left), int(top), int(right), int(bottom)))
    cw, ch = c.size
    if max(cw, ch) < 500:
        scale = int(500 / max(cw, ch)) + 1
        c = c.resize((cw * scale, ch * scale), Image.LANCZOS)
    c.save(outpath, quality=90)
    return (W, H, c.size)


for i, p in enumerate(pairs):
    for side in ("foto_a", "foto_b"):
        f = p[side]
        imgpath = os.path.join(base, f["imagem"])
        out = os.path.join(outdir, "p%02d_%s.jpg" % (i, side[-1]))
        info = crop(imgpath, f["regiao_pct"], out)
        print(i, side, f["imagem"], "->", os.path.basename(out), "img", info[:2], "crop", info[2])
