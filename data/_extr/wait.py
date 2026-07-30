import glob, time, os
d = '/Users/teste/encarteconcorrente/data/_extr'
for _ in range(200):
    files = [f for f in glob.glob(os.path.join(d, '*.json')) if os.path.basename(f) != 'specs.json']
    if len(files) >= 34:
        print('PRONTO', len(files))
        break
    time.sleep(5)
else:
    print('TIMEOUT', len(files))
files = [os.path.basename(f) for f in glob.glob(os.path.join(d, '*.json')) if os.path.basename(f) != 'specs.json']
print('n=', len(files))
