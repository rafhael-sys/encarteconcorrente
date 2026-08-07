import glob, os, time
BASE = os.path.dirname(os.path.abspath(__file__))
pat = os.path.join(BASE, 'data/_extract/sim0807_verd_*.json')
while len(glob.glob(pat)) < 5:
    time.sleep(3)
print("TODOS OS 5 ARQUIVOS DE VEREDITO PRONTOS")
for f in sorted(glob.glob(pat)):
    print(" ", os.path.basename(f))
