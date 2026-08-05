from PIL import Image
base = "/Users/teste/encarteconcorrente/"
out = base + "data/_extract/_crops/"
# Assai Above desodorante: product image sits above the text label at y59
img = Image.open(base + "data/pages/assai_168730-572_p1.jpg").convert("RGB")
W,H = img.size
box = (int(0.54*W), int(0.55*H), int(0.80*W), int(0.66*H))
c = img.crop(box)
c = c.resize((c.width*3, c.height*3))
c.save(out+"p4_b_zoom.png")

# Atacadao ONE Above for reference already have p4_a; make a zoom too
img2 = Image.open(base + "data/pages/atacadao_f6c7b8e8bd_p2.jpg").convert("RGB")
W2,H2 = img2.size
box2 = (int(0.60*W2), int(0.08*H2), int(0.98*W2), int(0.26*H2))
c2 = img2.crop(box2)
c2 = c2.resize((c2.width*2, c2.height*2))
c2.save(out+"p4_a_zoom.png")
print("ok")
