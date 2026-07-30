import glob, time, os
d = '/Users/teste/encarteconcorrente/data/_extr'
for _ in range(120):
    files = glob.glob(os.path.join(d, 'sim_out_*.json'))
    if len(files) >= 5:
        print('PRONTO', len(files)); break
    time.sleep(5)
else:
    print('TIMEOUT', len(files))
print('n=', len(glob.glob(os.path.join(d, 'sim_out_*.json'))))
