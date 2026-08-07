from PIL import Image
import os

base = 'data/pages'
jobs = [
    ('3957782811390174014', 0.60, 0.36, 0.98, 0.54, 'chuchu'),
    ('3957801333444952245', 0.28, 0.36, 0.88, 0.60, 'mamao'),
    ('3957783695259477698', 0.00, 0.02, 0.48, 0.22, 'ameixa'),
    ('3957802063565438500', 0.40, 0.30, 0.75, 0.55, 'melao479'),
]
out = 'data/_extract'
for sc, x0, y0, x1, y1, tag in jobs:
    p = os.path.join(base, f'story_miramarsupermercado_{sc}.jpg')
    im = Image.open(p)
    w, h = im.size
    box = (int(x0*w), int(y0*h), int(x1*w), int(y1*h))
    c = im.crop(box).resize((int((box[2]-box[0])*2), int((box[3]-box[1])*2)))
    o = os.path.join(out, f'_crop_{tag}.png')
    c.save(o)
    print(o, im.size)
