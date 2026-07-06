# Assaí Atacadista (assai.com.br) — Ofertas da loja Assaí Natal

Investigação feita em 06/07/2026, 4 requests via curl (sem browser).
Página analisada: `https://www.assai.com.br/ofertas/rio-grande-do-norte/assai-natal`

## (a) Viabilidade sem browser

**SIM, é viável — e é ainda mais simples que o Atacadão.** O site é Drupal 7 (tema
`assai_2024`). A página de ofertas vem com os containers vazios
(`.ofertas-tab`, `.ofertas-slider`, `.ofertas-tab-validade`) e o JS do tema
(agregado advagg) preenche tudo a partir de **um único arquivo JSON estático**:

```
https://www.assai.com.br/sites/default/files/static/ofertas_assai.json
```

- HTTP 200 com um simples curl + UA de Chrome. Sem cookie, sem token, sem captcha.
- Não há `__NEXT_DATA__`, Apollo, ld+json nem jsonapi — o Drupal só serve esse JSON.
- O JS oficial faz `GET .../ofertas_assai.json?<cachebuster>` (o cachebuster é só
  `AAAAMDDHHm` — qualquer string serve, ou nenhuma).

**Ressalva idêntica à do Atacadão:** o JSON **não tem produto+preço estruturado**.
Cada "oferta" é um ciclo de encarte (Jornal de Ofertas) com **período de validade**
e as **imagens JPEG das páginas do encarte** (CloudFront). Ou seja:

- **Validade do ciclo + imagens do encarte** → direto do JSON (100% sem browser).
- **Nome do produto + preço** → OCR/visão sobre os JPEGs das páginas (mesmo
  pipeline já usado no projeto para os outros encartes).

## Como a loja Natal é identificada

O HTML da página da loja traz `<section class="bloco-ofertas-tabloide"
data-nid="120" data-eid="19">`. Mas nem precisa baixar o HTML: o próprio
`ofertas_assai.json` tem a lista `lojas` com o mapeamento slug → ids:

| Campo | Valor (Assaí Natal) |
|---|---|
| `nid` (node id da loja) | `120` |
| `eid` (id do estado, RN) | `19` |
| `tid` (term id Drupal) | `42` |
| `loja_id` | `114` |
| `url` | `/ofertas/rio-grande-do-norte/assai-natal` |

Lógica de seleção (copiada do JS do tema, função `montaOfertas`): uma oferta vale
para a loja se `ofertas[i].lojas[]` contém um par `{eid:19, nid:120}`.

## (b) Comandos curl que FUNCIONAM

`UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"`

### 1. Baixar o JSON de ofertas (nacional, ~115 KB) — o principal

```bash
curl -sS -A "$UA" \
  "https://www.assai.com.br/sites/default/files/static/ofertas_assai.json" \
  -o ofertas_assai.json
```

### 2. Filtrar as ofertas vigentes da loja Natal (jq)

```bash
curl -sS -A "$UA" \
  "https://www.assai.com.br/sites/default/files/static/ofertas_assai.json" |
jq '[.ofertas[] | select(any(.lojas[]; .eid==19 and .nid==120))
     | {id, id_oferta, start_date, end_date, custom_text,
        images: [.images[].url]}]'
```

### 3. Baixar as páginas do encarte (JPEG público no CloudFront, ~1 MB/página)

```bash
curl -sS -A "$UA" -O \
  "https://d2q57q7k4hzryv.cloudfront.net/RPA/v3/48841/campanha-48841-cluster-564-pagina-1.jpeg"
```

Padrão da URL de imagem:
`https://d2q57q7k4hzryv.cloudfront.net/RPA/v3/{campanha}/campanha-{campanha}-cluster-{cluster}-pagina-{N}.jpeg`
(`id_oferta` no JSON = `{campanha}-{cluster}`). Bucket S3 público via CloudFront,
sem assinatura. `last-modified` das imagens indica quando o encarte foi gerado.

## Resultado real em 06/07/2026 (Natal, eid=19/nid=120)

3 jornais vigentes:

| id | id_oferta | validade | páginas |
|---|---|---|---|
| 24731 | 48934-564 | só 06/07/2026 (ofertas de 1 dia) | 1 |
| 24738 | 48841-564 | 06/07/2026 a 09/07/2026 | 4 |
| 24740 | 48995-564 | 06/07/2026 a 10/07/2026 | 1 |

## (c) Mapa de campos do JSON

Topo: `{ "ofertas": [...], "lojas": [...] }` (78 ofertas e 344 lojas no snapshot).

`ofertas[]` (um item = um ciclo de encarte):

| Campo | Significado | Exemplo |
|---|---|---|
| `id` | id interno Drupal da oferta | `"24738"` |
| `id_oferta` | `{campanha}-{cluster}` do sistema RPA | `"48841-564"` |
| `title` | título do jornal (frequentemente vazio) | `""` |
| `start_date` | **início da validade** (DD/MM/AAAA) | `"06/07/2026"` |
| `end_date` | **fim da validade** (DD/MM/AAAA) | `"09/07/2026"` |
| `custom_text` | texto de validade pronto p/ exibição | `"Preços válidos de 06/07/2026 até 09/07/2026"` |
| `origem` | fonte (`integracao` = automático) | `"integracao"` |
| `destaque` | ordenação (maior primeiro) | `"0"` |
| `lojas[]` | pares `{eid, nid}` das lojas atendidas | `{"eid":19,"nid":120}` |
| `images[].url` | **imagem JPEG de cada página do encarte** | CloudFront acima |

`lojas[]` (topo): `{tid, name, city_id, nid, eid, loja_id, url}` — usar para
resolver o slug de qualquer outra loja Assaí (mesmo pipeline serve para todas).

**Nome do produto / preço / unidade:** NÃO existem no JSON — estão renderizados
dentro dos JPEGs. Extração = OCR/visão sobre `images[].url` (validade vem do JSON,
então cada produto extraído herda `start_date`/`end_date` do seu jornal).

## (d) Bloqueios e observações

1. **Nenhum bloqueio de acesso**: HTML, JSON e imagens respondem 200 com UA de
   Chrome. Existe um script de bot-protection no `<head>` (path aleatório), mas
   não é exigido para o JSON estático nem para o CloudFront.
2. **Sem dado estruturado por produto** — este é o único bloqueio real para
   "nome+preço" direto de API. Testado `campanha-...-cluster-564.json` no
   CloudFront → 403 (não existe feed irmão das imagens).
3. O JSON é **nacional** (todas as lojas): 1 request/dia já cobre qualquer loja.
   Não martelar; o arquivo muda tipicamente 1x/dia (encartes de segunda-feira e
   ofertas diárias).
4. `ofertas_v1` existe no JS (`result.ofertas_v1`) mas veio vazio; o código atual
   (`fonteOferta()`) retorna sempre `ofertas` — ignorar `ofertas_v1`.
5. Datas em formato brasileiro DD/MM/AAAA (parsear com cuidado).
6. As imagens têm `content-type: binary/octet-stream` — salvar como `.jpeg`
   pelo nome do arquivo.
