# Nosso Atacarejo (nossoatacarejo.com.br) — Encartes da loja Assú/RN

Investigação feita em 09/07/2026 via GitHub Actions (curl + Chrome headless).
Página analisada: `https://www.nossoatacarejo.com.br/encarte/quarta-e-quinta-rn/5`

## (a) Viabilidade sem browser

**SIM, é viável.** O site é Next.js (App Router) com renderização no servidor:
um simples `curl` + User-Agent de Chrome devolve o HTML completo (~52 KB), sem
cookie, sem token, sem captcha. Não há API JSON separada — o catálogo de
encartes da loja vem **embutido no próprio HTML**, dentro dos scripts
`self.__next_f.push([1,"..."])` (payload RSC do Next.js).

Detalhe importante: a página de **qualquer** encarte da loja traz o array
`flyers` com **todos** os encartes da loja (não só o do slug da URL). Ou seja,
uma única requisição basta para ver tudo que está no ar.

## Identificadores de loja (`storeId` na URL)

O seletor da home (`<select name="states">` + `<select name="enterprises">`)
mapeia:

| Estado | storeId | Cidade |
|---|---|---|
| RN | 1 | Pau dos Ferros |
| RN | 2 | São Miguel |
| RN | 5 | **Assú** (a que monitoramos) |
| CE | — | Morada Nova, Quixadá, Limoeiro do Norte |

Os encartes do RN são estaduais (slugs terminam em `-rn` e a arte diz "Estado
do RN"), então monitorar a loja 5 cobre o estado.

## Formato de cada item de `flyers`

```json
{
 "id": "uuid fixo da campanha",
 "name": "Nossa Quarta & Quinta",
 "slug": "quarta-e-quinta-rn",
 "description": "Ofertas fresquinhas pra sua feira da semana!",
 "image_card_url": "https://cdn.nossoatacarejo.com.br/official-website/flyers/images/...",
 "images": [{"image_url": "https://cdn.nossoatacarejo.com.br/.../*.png", "alt_text": "...", "order": 0}],
 "status": "active",
 "start_date": "2026-07-08T06:00:00-03:00",
 "end_date": "2026-07-09T23:59:00-03:00"
}
```

Campanhas vistas no RN: `quarta-e-quinta-rn`, `nosso-final-de-semana-rn` e
`encarte-do-mes-rn`.

**Atenção (dedup):** o `id` do flyer é **fixo por campanha** — a cada ciclo
semanal eles trocam só `images`, `start_date` e `end_date` no mesmo registro
(prova: o `image_card_url` tem timestamp de out/2025 e a imagem vigente tem
timestamp atual). Por isso a chave de "já visto" no `collect_web.py` é
`nosso:{id}:{inicio}:{fim}`, e não o id sozinho.

- **Validade do ciclo + imagens do encarte** → direto do payload (100% sem browser).
- **Nome do produto + preço** → leitura das imagens (mesmo pipeline dos demais).
- As páginas são **PNG** no CDN (`cdn.nossoatacarejo.com.br`); o coletor
  converte para JPG na hora (`png_para_jpg`), que é o formato que o restante
  do projeto espera.

## Plano B

Se o curl for barrado um dia, o mesmo HTML sai do Chrome real via
`tools/fetch_pagina.js` (o payload `__next_f` continua no DOM renderizado) —
mesmo esquema do Atacadão.
