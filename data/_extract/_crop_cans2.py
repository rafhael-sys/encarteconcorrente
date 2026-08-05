from PIL import Image
base = "/Users/teste/encarteconcorrente/"
out = base + "data/_extract/_crops/"
img = Image.open(base + "data/pages/assai_168730-572_p1.jpg").convert("RGB")
W, H = img.size
box = (int(0.57 * W), int(0.49 * H), int(0.75 * W), int(0.55 * H))
c = img.crop(box)
c = c.resize((c.width * 7, c.height * 7))
c.save(out + "p4_b_cans2.png")
print("ok")
