# MyDoctor (projeto híbrido)

Estrutura igual ao [AppHibrido](https://github.com/ataides01/AppHibrido):

| Pasta | Função |
|-------|--------|
| **mydoctor-api/** | Backend Django (consultas, chat, receitas, admin) |
| **mydoctor/** | App móvel/web Expo (React Native) |

## mydoctor-api (Django)

```bash
cd mydoctor-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API em http://127.0.0.1:8000 — health: `/health/`

### Deploy na Vercel

1. Importar **pedronunes07/mydoctor2** → branch `main`
2. **Framework Preset:** **Django** (não use "Other")
3. **Root Directory:** clique em **Edit** e coloque `mydoctor-api` (não deixe `./`)
4. **Environment Variables** (Produção):
   - `SECRET_KEY` = uma chave longa aleatória
   - `DEBUG` = `False`
5. Clique em **Deploy** — no log deve aparecer commit recente e `Python 3.12`, não `Node.js 20.x`

Se mantiver Root Directory `./`, o `vercel.json` na raiz tenta instalar deps em `mydoctor-api/`, mas o preset **Django** + pasta `mydoctor-api` é o recomendado.

## mydoctor (Expo)

```bash
cd mydoctor
cp .env.example .env
npm install
npx expo start
```

No `.env`:

```
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
```

Android emulador: use `http://10.0.2.2:8000`. Celular na mesma rede: IP da máquina.

## Repositório

https://github.com/pedronunes07/mydoctor2
