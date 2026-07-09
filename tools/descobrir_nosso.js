#!/usr/bin/env node
/* TEMPORÁRIO — descoberta da API do nossoatacarejo.com.br.
   Abre a página do encarte num Chrome real e imprime as chamadas de rede
   (JSON/imagens) para entendermos de onde vêm as páginas do encarte.
   Uso: node descobrir_nosso.js <url> */
const { chromium } = require('playwright-core');

(async () => {
  const url = process.argv[2] || 'https://www.nossoatacarejo.com.br/encarte/quarta-e-quinta-rn/5';
  let browser;
  const guarda = setTimeout(async () => {
    console.error('[descobrir] tempo esgotado');
    if (browser) await browser.close().catch(() => {});
    process.exit(1);
  }, 110000);
  try {
    try {
      browser = await chromium.launch({ channel: 'chrome', headless: true });
    } catch (_) {
      browser = await chromium.launch({ headless: true });
    }
    const ctx = await browser.newContext({ locale: 'pt-BR', viewport: { width: 1366, height: 900 } });
    const page = await ctx.newPage();
    const jsons = [];
    page.on('response', async (resp) => {
      const ct = (resp.headers()['content-type'] || '').toLowerCase();
      const u = resp.url();
      if (ct.includes('json') || /\/api\//i.test(u)) {
        try {
          const body = await resp.text();
          jsons.push({ url: u, status: resp.status(), body: body.slice(0, 30000) });
        } catch (_) {}
      } else if (ct.includes('image') && !/\.(svg|ico|png)(\?|$)/i.test(u)) {
        console.log(`IMG ${resp.status()} ${u}`);
      }
    });
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(8000);
    console.log('=== JSON/API RESPONSES ===');
    for (const j of jsons) {
      console.log(`\n--- ${j.status} ${j.url}`);
      console.log(j.body);
    }
    console.log('\n=== IMGS RENDERIZADAS ===');
    for (const src of await page.$$eval('img', (els) => els.map((e) => e.src))) console.log(src);
    console.log('\n=== LINKS ===');
    for (const h of await page.$$eval('a', (els) => els.map((e) => e.href))) console.log(h);
    await browser.close();
    clearTimeout(guarda);
    process.exit(0);
  } catch (e) {
    console.error(`[descobrir] ${e.message}`);
    if (browser) await browser.close().catch(() => {});
    clearTimeout(guarda);
    process.exit(1);
  }
})();
