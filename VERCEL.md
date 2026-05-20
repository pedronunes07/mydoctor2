# Configurar Vercel — mydoctor2

## Settings → General

- **Root Directory:** deixe **vazio** (`./`) — o `vercel.json` na raiz já aponta para `mydoctor-api/`

## Settings → Build and Deployment

### Se aparecer Django no Framework Preset

- Preset: **Django**
- Root Directory: **`mydoctor-api`**
- Desligue overrides de Build e Output

### Se só tiver **Other** (seu caso)

Ative **Override** e configure:

| Campo | Valor |
|-------|--------|
| **Install Command** | `python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt` |
| **Build Command** | `cd mydoctor-api && python3 manage.py collectstatic --noinput` |
| **Output Directory** | *(vazio — apague `public`)* |

Salve e faça **Create Deployment** na branch `main` (commit mais recente).

## Variáveis de ambiente

- `SECRET_KEY` — chave aleatória longa
- `DEBUG` — `False`

## Conferir deploy correto

- Commit: `e14c9b9` ou mais novo (não `6ebc0ed`)
- Build demora mais que ~10s (instala Python + collectstatic)
- Site: https://mydoctor2-ten.vercel.app com CSS e layout My Doctor
