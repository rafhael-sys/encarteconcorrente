import json

def show(fp, npg_limit=None, nprod_limit=6):
    d = json.load(open(fp))
    print("====", d.get('shortcode'), "|", d.get('inicio'), "..", d.get('fim'), "|", d.get('titulo'))
    for k, v in d['pages'].items():
        if not v:
            continue
        print(f"  [{k}]  ({len(v)} prod)")
        for it in v[:nprod_limit]:
            print(f"     {it.get('p'):>10}  {it.get('u','')[:26]:26s}  {it.get('n')}")

show('data/_extract/w0807_story_redemaisrn_20260807.json')
print()
show('data/_extract/w0807_atacadao_0f996b2c97.json', nprod_limit=4)
print()
show('data/_extract/w0807_assai_169498-572.json', nprod_limit=5)
print()
show('data/_extract/w0807_story_atacarejo_santoantonio.ofc__B.json', nprod_limit=5)
