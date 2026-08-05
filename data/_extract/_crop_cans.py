from PIL import Image
base = "/Users/teste/encarteconcorrente/"
out = base + "data/_extract/_crops/"
img = Image.open(base + "data/pages/assai_168730-572_p1.jpg").convert("RGB")
W, H = img.size
box = (int(0.55 * W), int(0.485 * H), int(0.80 * W), int(0.565 * H))
c = img.crop(box)
c = c.resize((c.width * 4, c.height * 4))
c.save(out + "p4_b_cans.png")
print("ok", img.size)
