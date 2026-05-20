# Configurar Vercel — mydoctor2

## Por que aparece 404 NOT_FOUND?

Isso **não é causado pelo CSS**. A página 404 da Vercel aparece quando **Produção** está num deploy antigo (ex.: commit `6ebc0ed`) **sem** entrypoint Django/WSGI configurado. O build termina em ~4s e o site não sobe.

**Solução:** promover ou redeploy do commit mais recente (`main`).

## Settings → General

- **Root Directory:** `mydoctor-api` (recomendado)
- **Framework Preset:** **Django** (não use "Other")

Com isso, a Vercel usa `manage.py`, `pyproject.toml` (`[tool.vercel] entrypoint`) e roda `collectstatic` automaticamente. O `mydoctor-api/vercel.json` fica vazio de propósito.

## Settings → Build and Deployment

- Desligue **Substituições de produção** (aviso amarelo) — use as configurações do projeto
- **Incluir arquivos fora do diretório raiz:** pode ficar habilitado
- Não defina Output Directory (`public` deve estar vazio)

## Variáveis de ambiente (Production)

| Variável | Valor |
|----------|--------|
| `SECRET_KEY` | chave longa aleatória |
| `DEBUG` | `False` |

## Redeploy correto

1. **Deployments** → último deploy da branch `main` (não `6ebc0ed`)
2. **⋯** → **Redeploy** ou **Promote to Production**
3. Nos logs: **Python 3.12**, instalação de pacotes, `collectstatic` (build > ~15s)
4. Abra o domínio: deve carregar a home **My Doctor** com CSS em `/static/`

## Conferir

- Commit recente (não só manifesto Python na raiz)
- Home sem erro 404
- CSS carregando (F12 → Network → `style.css` status 200)
