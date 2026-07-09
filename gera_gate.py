#!/usr/bin/env python3
"""Gera o site publicado: index.html (porta com senha) + painel.enc.

Uso: gera_gate.py <painel.html> <dir_saida> <arquivo_senha>

O painel é criptografado com AES-256-CBC; a chave vem da senha via
PBKDF2-SHA256 (300 mil iterações). No site só vão o salt, o iv e o blob
criptografado — sem a senha ninguém lê nada. O bloco da engrenagem
(<!--CFG-INI--> … <!--CFG-FIM-->), que só existe no arquivo local,
é removido antes de criptografar.
"""
import base64
import hashlib
import os
import subprocess
import sys

ITERACOES = 300_000

def main():
    painel, outdir, senha_file = sys.argv[1], sys.argv[2], sys.argv[3]
    senha = open(senha_file, encoding='utf-8').read().strip()
    if len(senha) < 6:
        sys.exit('[gate] senha muito curta (mínimo 6 caracteres)')

    html = open(painel, 'rb').read()
    # blocos só-locais: engrenagem (CFG) e aba de logs (LOGS) nunca vão pro site
    for mi, mf in ((b'<!--CFG-INI-->', b'<!--CFG-FIM-->'),
                   (b'<!--LOGS-INI-->', b'<!--LOGS-FIM-->')):
        ini, fim = html.find(mi), html.find(mf)
        if ini != -1 and fim != -1:
            html = html[:ini] + html[fim + len(mf):]
    if (b'<!--CFG-INI-->' in html or b'cfgBtn' in html
            or b'<!--LOGS-INI-->' in html or b'logsAbrir' in html):
        sys.exit('[gate] bloco só-local (engrenagem/logs) ainda está no HTML — publicação abortada')

    salt, iv = os.urandom(16), os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, ITERACOES, dklen=32)
    cifra = subprocess.run(
        ['openssl', 'enc', '-aes-256-cbc', '-K', key.hex(), '-iv', iv.hex()],
        input=html, capture_output=True, check=True).stdout
    # salt e iv viajam no cabeçalho do próprio blob: uma aba aberta antes da
    # republicação diária continua conseguindo decifrar o painel novo
    enc = b'ENC1' + salt + iv + cifra
    open(os.path.join(outdir, 'painel.enc'), 'wb').write(enc)

    gate = GATE.replace('__ITER__', str(ITERACOES))
    open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8').write(gate)
    print(f'[gate] ok — painel.enc {len(enc)/1e6:.1f} MB')


GATE = '''<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Encartes</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%8F%B7%EF%B8%8F%3C/text%3E%3C/svg%3E">
<style>
  :root{
    --bg:#ffffff; --surface:#f9f9f9; --border:#e5e5e5;
    --text:#0d0d0d; --text-2:#5d5d5d; --text-3:#8f8f8f;
    --green:#10a37f; --green-bg:#e6f4ef; --red:#c0392b;
  }
  *{box-sizing:border-box}
  body{
    margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
    background:var(--bg);color:var(--text);
    font:400 15px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
  }
  .box{width:min(360px,calc(100vw - 48px));display:flex;flex-direction:column;align-items:center;gap:0}
  .mark{
    width:44px;height:44px;border-radius:13px;background:var(--green);
    display:flex;align-items:center;justify-content:center;margin-bottom:18px;
  }
  h1{font-size:19px;font-weight:650;letter-spacing:-.02em;margin:0 0 4px}
  .sub{font-size:13.5px;color:var(--text-3);margin:0 0 26px}
  form{width:100%;display:flex;flex-direction:column;gap:10px}
  input{
    width:100%;font:inherit;font-size:15px;color:var(--text);
    border:1px solid var(--border);border-radius:999px;padding:12px 18px;outline:none;
    background:var(--surface);transition:border-color .15s, box-shadow .15s, background .15s;
    text-align:center;
  }
  input:focus{background:var(--bg);border-color:var(--green);box-shadow:0 0 0 3px var(--green-bg)}
  button{
    font:inherit;font-size:14.5px;font-weight:600;color:#fff;background:var(--green);
    border:none;border-radius:999px;padding:12px 18px;cursor:pointer;
  }
  button:hover{filter:brightness(1.05)}
  button:disabled{opacity:.55;cursor:default}
  .erro{color:var(--red);font-size:13px;min-height:20px;margin-top:10px;text-align:center}
  .prog{width:100%;margin-top:14px;display:none}
  .prog.on{display:block}
  .prog .track{height:4px;border-radius:4px;background:var(--border);overflow:hidden}
  .prog .fill{height:100%;width:0%;border-radius:4px;background:var(--green);transition:width .2s}
  .prog .txt{font-size:12.5px;color:var(--text-3);text-align:center;margin-top:8px}
  footer{position:fixed;bottom:22px;left:0;right:0;text-align:center;font-size:12px;color:var(--text-3)}
</style>
<body>
<div class="box">
  <span class="mark"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.3 9.3a2 2 0 0 0 2.8 0l7.2-7.2a2 2 0 0 0 0-2.8L12 2z"/><circle cx="7.5" cy="7.5" r="1.4" fill="#fff" stroke="none"/></svg></span>
  <h1>Encartes</h1>
  <p class="sub">Painel diário</p>
  <form id="f">
    <input id="senha" type="password" placeholder="Senha de acesso" autocomplete="current-password" autofocus>
    <button id="entrar" type="submit">Entrar</button>
  </form>
  <div class="erro" id="erro"></div>
  <div class="prog" id="prog">
    <div class="track"><div class="fill" id="fill"></div></div>
    <div class="txt" id="ptxt">Baixando o painel…</div>
  </div>
</div>
<script>
/* Tudo dentro de uma função: document.open() reaproveita a janela, e
   declarações soltas aqui (ex.: const $) colidiriam com as do painel
   escrito, matando o script dele com "already been declared". */
(() => {
const ITER=__ITER__;
const $ = id => document.getElementById(id);

let encCache = null;
async function baixar(){
  if(encCache) return encCache;
  /* 'no-cache' (e não 'no-store'): o navegador PERGUNTA ao servidor se o
     painel mudou. Não mudou -> reusa o download anterior e abre na hora;
     mudou -> baixa a versão nova. Nunca mostra painel velho, e as reaberturas
     do dia deixam de baixar ~45 MB à toa. */
  const resp = await fetch('painel.enc', {cache:'no-cache'});
  if(!resp.ok) throw new Error('rede');
  const total = +resp.headers.get('content-length') || 0;
  const chunks = []; let got = 0;
  const reader = resp.body.getReader();
  while(true){
    const {done, value} = await reader.read();
    if(done) break;
    chunks.push(value); got += value.length;
    if(total) $('fill').style.width = Math.round(100*got/total) + '%';
  }
  const enc = new Uint8Array(got); let o = 0;
  for(const c of chunks){ enc.set(c, o); o += c.length; }
  encCache = enc;
  return enc;
}

async function abrir(senha){
  $('prog').classList.add('on'); $('ptxt').textContent = 'Baixando o painel…';
  const blob = await baixar();
  $('fill').style.width = '100%'; $('ptxt').textContent = 'Abrindo…';
  /* cabeçalho do blob: 'ENC1' + salt(16) + iv(16) + dados cifrados */
  if(blob.length < 37 || new TextDecoder().decode(blob.slice(0,4)) !== 'ENC1') throw new Error('rede');
  const salt = blob.slice(4,20), iv = blob.slice(20,36), dados = blob.slice(36);
  const km = await crypto.subtle.importKey('raw', new TextEncoder().encode(senha), 'PBKDF2', false, ['deriveKey']);
  const key = await crypto.subtle.deriveKey(
    {name:'PBKDF2', salt, iterations:ITER, hash:'SHA-256'},
    km, {name:'AES-CBC', length:256}, false, ['decrypt']);
  let plano;
  try{ plano = await crypto.subtle.decrypt({name:'AES-CBC', iv}, key, dados); }
  catch(e){ throw new Error('senha'); }
  const txt = new TextDecoder().decode(plano);
  if(!txt.startsWith('<meta charset')) throw new Error('senha');
  /* guarda a senha COM a hora — usada pela regra de validade de 3h no rodapé do script */
  try{ localStorage.setItem('painel_senha', JSON.stringify({s: senha, t: Date.now()})); }catch(e){}
  document.open(); document.write(txt); document.close();
}

async function tentar(senha, silencioso){
  $('erro').textContent = ''; $('entrar').disabled = true;
  try{ await abrir(senha); }
  catch(e){
    $('prog').classList.remove('on'); $('fill').style.width = '0%';
    $('entrar').disabled = false;
    if(e.message === 'senha'){
      if(!silencioso){ $('erro').textContent = 'Senha incorreta — tente de novo.'; }
      try{ localStorage.removeItem('painel_senha'); }catch(x){}
    } else {
      $('erro').textContent = 'Não deu para baixar o painel — confira a internet e tente de novo.';
    }
    $('senha').focus();
  }
}

$('f').addEventListener('submit', e => {
  e.preventDefault();
  const s = $('senha').value;
  if(s) tentar(s, false);
});

/* destrava sozinho: senha salva neste navegador ou embutida no link (#senha).
   O trecho após # nunca é enviado ao servidor. A senha lembrada VENCE após
   3 horas sem uso — aí é preciso digitar de novo; cada acesso renova o prazo
   (o setItem do abrir() regrava a hora a cada entrada bem-sucedida). */
const VALIDADE_MS = 3*60*60*1000;
function senhaSalva(){
  let obj = null;
  try{ obj = JSON.parse(localStorage.getItem('painel_senha')); }catch(e){}
  /* qualquer coisa fora do formato atual {s, t} — inclusive a senha crua do
     formato antigo — é descartada: a pessoa digita uma única vez e o abrir()
     regrava no formato novo. (Aceitar o formato antigo era traiçoeiro: uma
     senha só de números passa no JSON.parse e viraria número, não texto.) */
  if(!obj || typeof obj.s !== 'string' || Date.now() - (obj.t || 0) > VALIDADE_MS){
    localStorage.removeItem('painel_senha');
    return null;
  }
  return obj.s;
}
try{
  const salva = senhaSalva();
  if(salva) tentar(salva, true);
  else if(location.hash.length > 1) tentar(decodeURIComponent(location.hash.slice(1)), true);
}catch(e){}
})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    main()
