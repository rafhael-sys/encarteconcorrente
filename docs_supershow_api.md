# Rede Super Show (redesupershow.com.br) — Coleta Web de Encartes

Documentação da descoberta técnica realizada para a esteira de inteligência.

## 1. Estrutura do Site e Viabilidade

* **Plataforma:** WordPress (Astra Theme + Spectra/UAGB) em `https://redesupershow.com.br`.
* **Sem Autenticação/Sem Captcha:** Acessível diretamente via `curl` com User-Agent de navegador (requer header User-Agent para evitar HTTP 406).
* **Formato dos Encartes:** PDFs digitais semanais e imagens PNG/WebP em alta resolução (1080x1350) hospedados em `wp-content/uploads/`.

## 2. Localização dos Encartes no HTML

Na home do site, o encarte vigente é inserido em blocos com link direto para o PDF:
```html
<figure class="wp-block-image alignfull size-full">
  <a href="https://redesupershow.com.br/wp-content/uploads/AAAA/MM/JOB-...-Encarte-Digital-...pdf">
    <img ...>
  </a>
</figure>
```

## 3. Pipeline de Processamento

1. O script faz `curl -sL --compressed -A UA https://redesupershow.com.br/`.
2. Extrai os links de PDF com regex `href="(https?://redesupershow.com.br/wp-content/uploads/[^"]+\.pdf)"`.
3. Se a URL ainda não foi vista em `data/posts_vistos.json`, baixa o arquivo `.pdf`.
4. Converte o PDF em JPGs nítidos de 1600px via conversor nativo do projeto (`tools/pdf2jpg` / `pdf2jpg.py`).
5. Cadastra o ciclo em `data/fila_novos.json` com `banner: "Rede Super Show"` e `segmento: "varejo"`.
