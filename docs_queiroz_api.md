# Queiroz Atacadão (grupoqrz.com.br) — Coleta Web de Encartes

Documentação da descoberta técnica realizada para a esteira de inteligência.

## 1. Estrutura do Site e Viabilidade

* **Plataforma:** WordPress no portal do Grupo QRZ (`https://grupoqrz.com.br`).
* **Seção de Encartes:** Localizada em `https://grupoqrz.com.br/#encarte`.
* **Sem Autenticação/Sem Captcha:** A página é HTML estático servido por Apache, acessível via `curl` com User-Agent de navegador padrão.
* **Formato dos Encartes:** Arquivos PDF diagramados em alta resolução hospedados em `wp-content/uploads/`.

## 2. Mapeamento das Praças do RN

O HTML da home contém seletores de estado e cidades com classes CSS dedicadas para cada loja/praça do Rio Grande do Norte:

| Classe CSS no HTML | Região Atendida no RN |
|---|---|
| `.qaParnamirim` | Parnamirim / Grande Natal |
| `.qaJoaoCamaraCearaMirimSaoGoncalo` | João Câmara, Ceará-Mirim e São Gonçalo do Amarante |
| `.qaMossoroAssu` | Mossoró e Assú |
| `.hqRN` | Hiper Queiroz / Lojas RN |

Dentro de cada contêiner, o botão de download possui o link direto:
```html
<div class="qaParnamirim">
  <a class="pdf-download-button" href="https://grupoqrz.com.br/wp-content/uploads/AAAA/MM/QA-...pdf" download>
</div>
```

## 3. Pipeline de Processamento

1. O script faz `curl -sL --compressed -A UA https://grupoqrz.com.br/`.
2. Extrai as URLs dos PDFs das classes do RN.
3. Se a URL ainda não foi vista em `data/posts_vistos.json`, baixa o arquivo `.pdf`.
4. Converte cada página do PDF em imagem JPG nítida de 1600px via conversor nativo do projeto (`tools/pdf2jpg` no macOS ou `tools/pdf2jpg.py` na nuvem).
5. Cadastra o ciclo em `data/fila_novos.json` com `banner: "Queiroz Atacadão"` e `segmento: "atacarejo"`.
