#!/usr/bin/env node
/* TEMPORÁRIO — sonda do nossoatacarejo.com.br (v2).
   1) Na home: abre o seletor de loja, lista estados/cidades e confirma uma
      loja do RN para descobrir a URL/lista de encartes da loja.
   2) Na página do encarte: imprime os scripts embutidos com dados do flyer. */
const { chromium } = require('playwright-core');

(async () => {
  let browser;
  const guarda = setTimeout(async () => {
    console.error('[descobrir] tempo esgotado');
    if (browser) await browser.close().catch(() => {});
    process.exit(1);
  }, 150000);
  try {
    try {
      browser = await chromium.launch({ channel: 'chrome', headless: true });
    } catch (_) {
      browser = await chromium.launch({ headless: true });
    }
    const ctx = await browser.newContext({ locale: 'pt-BR', viewport: { width: 1366, height: 900 } });
    const page = await ctx.newPage();
    page.on('response', async (resp) => {
      const ct = (resp.headers()['content-type'] || '').toLowerCase();
      if (ct.includes('json')) {
        try {
          console.log(`\nJSON ${resp.status()} ${resp.url()}`);
          console.log((await resp.text()).slice(0, 20000));
        } catch (_) {}
      }
    });

    console.log('##### HOME: seletor de loja');
    await page.goto('https://www.nossoatacarejo.com.br/', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(3000);
    for (const sel of await page.$$('select')) {
      console.log('SELECT html:', (await sel.evaluate((e) => e.outerHTML)).slice(0, 3000));
    }
    // se não houver <select>, mostra o HTML do modal para entender o componente
    const modal = await page.$('[role=dialog], .modal, form');
    if (modal) console.log('MODAL html:', (await modal.evaluate((e) => e.outerHTML)).slice(0, 6000));
    // tenta escolher RN e a primeira cidade
    try {
      const selects = await page.$$('select');
      if (selects.length >= 2) {
        const ops = await selects[0].$$eval('option', (os) => os.map((o) => `${o.value}|${o.textContent}`));
        console.log('ESTADOS:', ops.join(' ; '));
        const rn = ops.find((o) => /rio grande do norte|(^|\|)RN/i.test(o));
        if (rn) {
          await selects[0].selectOption(rn.split('|')[0]);
          await page.waitForTimeout(2500);
          const cid = await selects[1].$$eval('option', (os) => os.map((o) => `${o.value}|${o.textContent}`));
          console.log('CIDADES RN:', cid.join(' ; '));
          const cidade = cid.find((o) => o.split('|')[0] !== '');
          if (cidade) {
            await selects[1].selectOption(cidade.split('|')[0]);
            await page.waitForTimeout(1500);
            const btn = await page.$('button:has-text("Confirmar")');
            if (btn) {
              await btn.click();
              await page.waitForTimeout(6000);
              console.log('URL após confirmar:', page.url());
              console.log('LINKS após confirmar:');
              for (const h of await page.$$eval('a', (els) => els.map((e) => e.href))) {
                if (/encarte/i.test(h)) console.log(' ', h);
              }
              const htmlHome = await page.content();
              const m = htmlHome.match(/.{200}flyers.{600}/gi) || [];
              for (const t of m.slice(0, 6)) console.log('TRECHO flyers:', t.replace(/\n/g, ' ').slice(0, 800));
            } else console.log('botão Confirmar não encontrado');
          }
        }
      } else console.log(`só ${selects.length} <select> na home`);
    } catch (e) {
      console.log('interação com seletor falhou:', e.message);
    }

    console.log('\n##### PÁGINA DO ENCARTE: scripts embutidos');
    await page.goto('https://www.nossoatacarejo.com.br/encarte/quarta-e-quinta-rn/5', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(4000);
    const html = await page.content();
    for (const termo of ['flyer', 'valid', 'encarte']) {
      const re = new RegExp(`.{200}${termo}.{600}`, 'gi');
      const ms = html.match(re) || [];
      for (const t of ms.slice(0, 6)) console.log(`TRECHO ${termo}:`, t.replace(/\n/g, ' ').slice(0, 820));
    }
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
