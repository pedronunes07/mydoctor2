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

1. Novo projeto → repositório **mydoctor2**
2. **Root Directory:** `mydoctor-api`
3. **Framework Preset:** Django
4. Variáveis: `SECRET_KEY`, `DEBUG=False`

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
