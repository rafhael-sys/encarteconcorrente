from PIL import Image
im = Image.open('data/pages/story_miramarsupermercado_3957801333444952245.jpg')
w, h = im.size
# tighter around left tag price
box = (int(0.33*w), int(0.42*h), int(0.55*w), int(0.56*h))
c = im.crop(box)
c = c.resize((c.width*5, c.height*5))
c.save('data/_extract/_crop_mamao2.png')
print(im.size, box)
