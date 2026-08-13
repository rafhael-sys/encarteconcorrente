import glob, os
have = {os.path.basename(f).replace('w0812_', '').replace('.json', '')
        for f in glob.glob('data/_extract/w0812_*.json')}
need = ['Db82gnbnc9K', 'Db8W6CwF1uV', 'Db8VDKjFfxX', 'Db8TupgnB93', 'Db8Lfvwjlg7',
        'Db8__jomvzf', 'Db9nnfNm-SB', 'Db9mA_lG5wy', 'Db9gv6Dm77a', 'Db9fJfSmx32',
        'Db9TFhPn0tA', 'Db8Svn-SXFG', 'Db6hVuTMB4b', 'Db7tnmRADgl', 'Db9AfcOidEE',
        'Db8SbV6MFIu', 'Db4BsEcoMR0', 'Db9RIfbGqMd', 'Db6bIj6G7i0', 'atacadao_8b44a0d2fc']
missing = [s for s in need if s not in have]
print('extracts missing:', missing if missing else 'NONE - all 20 done')
for s in ['simverd_a', 'simverd_b', 'simincerto_a', 'simincerto_b']:
    print(s, os.path.exists(f'data/_extract/{s}.json'))
