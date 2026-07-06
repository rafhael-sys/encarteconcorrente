# Atacadão (atacadao.com.br) — API de produtos/ofertas para a loja Natal-Sul

Investigação feita em 06/07/2026, ~10 requests via curl (sem browser).

## (a) Viabilidade sem browser

**SIM, é viável.** O site é Next.js sobre VTEX (conta `atacadaobr`). As APIs públicas VTEX
respondem direto no domínio `www.atacadao.com.br` com um simples `curl` + User-Agent de
Chrome — sem cookie, sem token, sem captcha. Preço é **regionalizado**: passa-se um
`regionId` e o preço retornado muda por região (provado abaixo: mesmo produto R$ 2,89 em
Natal vs R$ 2,99 em São Paulo).

**Ressalva importante sobre "ofertas":** o e-commerce NÃO expõe as ofertas do encarte
como coleção/cluster com preço riscado (`ListPrice` == `Price` em tudo que amostramos,
`teasers` vazios). O encarte semanal da loja física é publicado como **flyer PDF** com
período de validade, via API da Carrefour (ver seção "Flyers/Encartes"). Ou seja:

- **Preço atual por produto na região de Natal** → API intelligent-search (funciona 100%).
- **Lista "produtos do encarte + validade"** → vem dos flyers PDF do storeInfo (precisa
  OCR/parse do PDF), ou cruzando os produtos do PDF com a busca por preço regional.

## Identificadores da loja Natal-Sul

Extraídos do `__NEXT_DATA__` de `https://www.atacadao.com.br/loja/natal-sul`
(rota Next `/loja/[slug]`, `props.pageProps.storeInfo`):

| Campo | Valor |
|---|---|
| storeId | `51` |
| seller VTEX (white-label) | `atacadaobr51` (nome: "Natal Sul") |
| CEP da loja | `59066-180` (Av. Dão Silveira 7796, Pitimbu, Natal-RN) |
| **regionId** (o que importa p/ preço) | `v2.72BBE3394D2C30D687E5FB8CE994FF62` |
| salesChannel (sc) | `1` (único observado) |

O `regionId` é obtido pela API de regiões do checkout a partir de qualquer CEP atendido
pela loja (não é o base64 `SW#atacadaobr51` — esse formato foi testado e ignorado):

```bash
curl -sL -A "Mozilla/5.0 ... Chrome/126.0.0.0 Safari/537.36" \
  "https://www.atacadao.com.br/api/checkout/pub/regions?country=BRA&postalCode=59066-180"
# -> [{"id":"v2.72BBE3394D2C30D687E5FB8CE994FF62","sellers":[...,{"id":"atacadaobr51","name":"Natal Sul"},...]}]
```

Nota: a região é uma área que contém vários sellers (`atacadaobr51` = Natal Sul entre
eles); o preço retornado pela busca é o preço regional (o JSON da busca mostra
`sellerId: "1"` / "ATACADAO SA", mas o valor muda conforme o `regionId`).

## (b) Comandos curl que FUNCIONAM

`UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"`

### 1. Busca de produto com preço regional de Natal (intelligent-search) — o principal

```bash
curl -sL -A "$UA" \
  "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/product_search/v2?query=creme%20de%20leite&count=10&hideUnavailableItems=true&regionId=v2.72BBE3394D2C30D687E5FB8CE994FF62"
```

- HTTP 200, JSON. `hideUnavailableItems=true` também restringe ao sortimento disponível
  na região (ex.: "arroz" caiu de 621 para 60 itens).
- Paginação: `&page=N` (a resposta traz `pagination`). Ordenação: `&sort=price:asc`,
  `discount:desc`, `orders:desc` etc.
- Filtro por categoria/cluster como facet no path:
  `.../product_search/category-1/mercearia?...` ou
  `.../product_search/productClusterIds/302?...` (ex. cluster 302 = "Mais Vendidos";
  clusters de cada produto vêm no campo `productClusters`).

### 2. Facets (para descobrir categorias/clusters)

```bash
curl -sL -A "$UA" \
  "https://www.atacadao.com.br/api/io/_v/api/intelligent-search/facets/category-1/mercearia?regionId=v2.72BBE3394D2C30D687E5FB8CE994FF62"
```
(com `query=` vazio e sem facet no path retorna `facets: []`).

### 3. API clássica de catálogo (também aberta, mas SEM preço regional)

```bash
curl -sL -A "$UA" \
  "https://www.atacadao.com.br/api/catalog_system/pub/products/search?_from=0&_to=9&fq=productClusterId:302"
```
HTTP 206, JSON clássico VTEX. Útil p/ catálogo/EAN; para preço use a #1.

### 4. Flyers/Encartes da loja (nomes de campanha + validade + PDF)

O HTML de `https://www.atacadao.com.br/loja/natal-sul` traz no `__NEXT_DATA__`
(`props.pageProps.storeInfo.flyers[]`) e o PDF é servido sem auth:

```bash
# baixar o PDF do encarte vigente (id vem do storeInfo.flyers[].id)
curl -sL -A "$UA" -o encarte.pdf \
  "https://apigw.cloud.carrefour.com.br/api-middleware-flyer-services/api/v2/Flyer/?id=1xocZO_MnGFlCvqTsjq3QD_BjIQ7N95an"
```

Exemplo real capturado (06/07/2026): flyer "Super Ofertas",
`validity.initial: 2026-07-06`, `validity.final: 2026-07-12`; além de "Fim de Semana",
"Açougue / Padaria / Frios e Fatiados" etc. Também existe o endpoint Next
`https://www.atacadao.com.br/_next/data/<buildId>/loja/natal-sul.json?slug=natal-sul`
(buildId atual `mEOna5Vls4fubrAHuEHQ0`, muda a cada deploy — mais robusto é dar GET na
página e extrair o `<script id="__NEXT_DATA__">`).

## (c) Campos JSON relevantes (intelligent-search)

Caminho por produto em `products[]`:

| Dado | Campo |
|---|---|
| Nome | `products[].productName` |
| Marca | `products[].brand` |
| SKU/EAN | `products[].items[].itemId` / `products[].items[].ean` |
| **Preço à vista (regional)** | `products[].items[].sellers[].commertialOffer.Price` |
| Preço "de" (riscado) | `...commertialOffer.ListPrice` (observado sempre == Price) |
| Preço sem desconto | `...commertialOffer.PriceWithoutDiscount` |
| Disponibilidade | `...commertialOffer.AvailableQuantity` / `IsAvailable` |
| "Validade" do preço | `...commertialOffer.PriceValidUntil` — **atenção**: é timestamp de cache da simulação (~1 ano à frente), NÃO é a validade da oferta do encarte |
| Promo/teaser (leve X pague Y etc.) | `...commertialOffer.teasers[]` (vazio nas amostras) |
| Clusters/coleções | `products[].productClusters[]` (`{id, name}`) |
| Link do produto | `products[].linkText` (slug) |

**Validade de oferta de encarte** só existe nos flyers: `storeInfo.flyers[].validity.{initial,final}`.

### Prova (respostas reais, 06/07/2026)

Com `regionId=v2.72BBE3394D2C30D687E5FB8CE994FF62` (Natal-Sul):

| Produto | Preço Natal | Preço SP (`v2.F89C0F0BD3AC1FE0C5C64FDFEA1DBD94`) |
|---|---|---|
| Creme de Leite Piracanjuba 200g | **R$ 2,89** | R$ 2,99 |
| Leite Condensado Piracanjuba Semidesnatado 395g | **R$ 5,59** | — |
| Arroz Branco Camil Tipo 1 1kg | **R$ 4,59** | — |
| Óleo de Soja Soya 900ml | **R$ 7,99** | — |

## (d) Bloqueios / limitações

- **Nenhum bloqueio de acesso**: sem auth, sem captcha, sem verificação de cookie/JS;
  respondeu a curl de IP residencial com UA de Chrome. (Não testado de datacenter.)
- **Não há coleção "ofertas do encarte" no e-commerce**: `ListPrice` nunca > `Price` e
  `teasers` vazios nas amostras; `sort=discount:desc` não revela promoções. A fonte da
  verdade das ofertas semanais é o **PDF do flyer** (com validade), que exige
  OCR/parse de PDF para extrair item+preço — ou usar a busca regional (#1) para obter o
  preço vigente de cada produto de interesse.
- `regionId` não aparece ecoado no `proxyUrl` da resposta, mas o efeito no preço é real
  (teste A/B acima). O parâmetro em query string funciona; o formato base64
  (`SW#atacadaobr51` → `U1cjYXRhY2FkYW9icjUx`) foi ignorado — usar sempre o `v2.…`.
- O GraphQL FastStore (`/api/graphql?operationName=ClientManyProductsQuery`) retorna
  HTTP 400 — o front é build custom; ignorar e usar o REST intelligent-search.
- `buildId` do Next muda a cada deploy — não fixar URLs `/_next/data/...`.
- Cortesia: manter poucas requisições com `sleep` entre elas; o catálogo tem ~8k itens
  disponíveis por região (`recordsFiltered: 8165` com query vazia + região Natal).
