#!/usr/bin/env python3
"""Coleta os STORIES (efêmeros, 24h) dos perfis — EXIGE cookie logado.

O feed é anônimo (collect.py); já os stories só aparecem para quem está logado,
então ficam neste script à parte, usando o cookie de ~/.config/ig_cookie.

Diferenças em relação ao feed:
  - endpoint  .../feed/user/{user_id}/story/  (com Cookie + x-ig-app-id)
  - sem legenda -> NÃO dá pra filtrar por palavra-chave; baixamos os frames e a
    revisão/extração decide o que é oferta (igual ao feed hoje, na mão)
  - efêmero -> precisa rodar todo dia; cada frame vira "página" na fila
  - dedup por 'pk' do frame (story_<pk>) para não re-baixar no mesmo dia

Uso:
  collect_stories.py          coleta de verdade (grava fila/vistos/status)
  collect_stories.py --dry    só busca e reporta (não grava nada) — seguro rodar
                              em paralelo com a coleta de feed
"""
import json, os, sys, time, random, datetime
import collect  # reusa: fetch_profile (anônimo, p/ pegar o user_id), download, helpers, UA/APP_ID/COOKIE

BASE, DATA, PAGES = collect.BASE, collect.DATA, collect.PAGES
UA, APP_ID, COOKIE = collect.UA, collect.APP_ID, collect.COOKIE


def fetch_story(user_id, tentativas=3):
    """Story do usuário (efêmero). Devolve o JSON da API; {} em resposta vazia."""
    ultimo = None
    for t in range(1, tentativas + 1):
        r = collect.sh(['curl', '-sk', '--compressed', '-A', UA,
                        '-H', f'x-ig-app-id: {APP_ID}',
                        '-H', f'Cookie: {COOKIE}',
                        f'https://i.instagram.com/api/v1/feed/user/{user_id}/story/'])
        try:
            if not r.stdout.strip():
                raise ValueError('resposta vazia (rate-limit ou cookie inválido)')
            return json.loads(r.stdout)
        except (json.JSONDecodeError, ValueError) as e:
            ultimo = e
            if t == tentativas:
                raise
            time.sleep(4 * t + random.uniform(0, 3))
    raise ultimo


def melhor_img(item):
    """URL da maior imagem do frame (ou None se for vídeo puro sem imagem)."""
    cands = (item.get('image_versions2') or {}).get('candidates') or []
    if not cands:
        return None
    return max(cands, key=lambda c: c.get('width', 0) * c.get('height', 0)).get('url')


def main():
    dry = '--dry' in sys.argv[1:]
    if not COOKIE:
        sys.exit('[story] sem cookie (~/.config/ig_cookie ou $IG_COOKIE) — story exige login. Abortei.')

    profiles = json.load(open(os.path.join(BASE, 'profiles.json')))
    seen   = set(collect.load_json(os.path.join(DATA, 'posts_vistos.json'), []))
    fila   = collect.load_json(os.path.join(DATA, 'fila_novos.json'), [])
    status = collect.load_json(os.path.join(DATA, 'coleta_status.json'), {})
    hoje  = datetime.date.today().isoformat()
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    novos = 0
    com_story = 0

    ordem = list(profiles)
    random.shuffle(ordem)
    for p in ordem:
        user, fonte = p['username'], p.get('banner', p['username'])
        try:
            uid = collect.fetch_profile(user)['id']   # anônimo, só p/ o id
            d = fetch_story(uid)
        except Exception as e:
            print(f'[erro] story {user}: {e}', file=sys.stderr)
            time.sleep(random.uniform(7, 14)); continue

        items = (d.get('reel') or {}).get('items') or []
        if not items:
            print(f'  {fonte}: sem story ativo')
            time.sleep(random.uniform(7, 14)); continue
        com_story += 1

        files = []
        for it in items:
            pk = str(it.get('pk') or it.get('id') or '')
            sid = f'story_{pk}'
            if sid in seen:
                continue
            url = melhor_img(it)
            if not url:                 # frame só de vídeo — marca visto e pula
                if not dry: seen.add(sid)
                continue
            fn = f'story_{user}_{pk}.jpg'
            if dry:
                files.append(fn)        # no dry não baixa, só conta
            elif collect.download(url, os.path.join(PAGES, fn)):
                files.append(fn); seen.add(sid)
            time.sleep(0.3)

        print(f'  {fonte}: {len(items)} frame(s) no story, {len(files)} novo(s)')
        if files and not dry:
            sc = f'story_{user}_{hoje.replace("-", "")}'
            existe = next((x for x in fila if x.get('shortcode') == sc), None)
            if existe:
                existe['paginas'].extend(f for f in files if f not in existe['paginas'])
            else:
                item = {
                    'shortcode': sc, 'perfil': user, 'banner': p['banner'],
                    'segmento': p['segmento'], 'caption': '',
                    'taken_at': items[0].get('taken_at', 0),
                    'carrossel': len(files) > 1, 'paginas': files,
                    'coletado_em': hoje, 'fonte': 'story',
                }
                if p.get('regra'):
                    item['regra'] = p['regra']
                fila.append(item)
            novos += len(files)
        status.setdefault(fonte, {})['ultimo_story_ok'] = agora
        time.sleep(random.uniform(7, 14))

    if not dry:
        collect.save_json(os.path.join(DATA, 'posts_vistos.json'), sorted(seen))
        collect.save_json(os.path.join(DATA, 'fila_novos.json'), fila)
        collect.save_json(os.path.join(DATA, 'coleta_status.json'), status)

    modo = 'DRY (nada gravado)' if dry else 'gravado'
    print(f'\n{novos} frame(s) de story novos ({com_story} perfis com story) — {modo}')


if __name__ == '__main__':
    main()
