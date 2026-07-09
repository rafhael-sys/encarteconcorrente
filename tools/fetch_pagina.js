#!/usr/bin/env node
/* Plano B da coleta: abre a página num Chrome DE VERDADE (o instalado no Mac,
   via playwright-core) e imprime o HTML no stdout. Um navegador real passa
   pelos desafios anti-robô (Cloudflare) que barram o curl de vez em quando.

   Orçamento interno total ~65s — sempre MENOR que o timeout de quem chama
   (150s no collect_web.py), para o processo sair limpo e nunca deixar um
   Chrome órfão. O watchdog de 110s é o último recurso.

   Uso: node fetch_pagina.js <url> [seletor_de_espera]
   Sai com código 0 e HTML no stdout; código 1 em falha (mensagem no stderr). */
const { chromium } = require('playwright-core');

(async () => {
  const url = process.argv[2];
  const espera = process.argv[3] || null;
  if (!url) { console.error('uso: fetch_pagina.js <url> [seletor]'); process.exit(1); }
  let browser;
  const guarda = setTimeout(async () => {
    console.error('[fetch_pagina] tempo esgotado (watchdog)');
    if (browser) await browser.close().catch(() => {});
    process.exit(1);
  }, 110000);
  try {
    browser = await chromium.launch({ channel: 'chrome', headless: true });
    const ctx = await browser.newContext({
      locale: 'pt-BR',
      viewport: { width: 1366, height: 900 },
    });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    if (espera) {
      await page.waitForSelector(espera, { state: 'attached', timeout: 20000 });
    }
    const html = await page.content();
    // escrita AGUARDADA: process.exit logo após write truncaria HTML grande
    await new Promise((res, rej) => process.stdout.write(html, e => e ? rej(e) : res()));
    await browser.close();
    clearTimeout(guarda);
    process.exit(0);
  } catch (e) {
    console.error(`[fetch_pagina] ${e.message}`);
    if (browser) await browser.close().catch(() => {});
    clearTimeout(guarda);
    process.exit(1);
  }
})();
