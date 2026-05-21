# Configurar Vercel — mydoctor2

## Por que aparece 404 NOT_FOUND?

Isso **não é causado pelo CSS**. A página 404 da Vercel aparece quando **Produção** está num deploy antigo (ex.: commit `6ebc0ed`) **sem** entrypoint Django/WSGI configurado. O build termina em ~4s e o site não sobe.

**Solução:** promover ou redeploy do commit mais recente (`main`).

## Settings → General

- **Root Directory:** `mydoctor-api` (recomendado)
- **Framework Preset:** **Django** (não use "Other")

### Se o preset for **Other** (seu caso no print)

O `mydoctor-api/vercel.json` já define install, build, WSGI e rotas — **não** use Redeploy do deploy antigo `6ebc0ed`.

1. **Substituições de produção:** remova (use configurações do projeto)
2. **Root Directory:** `mydoctor-api`
3. Em **Deployments** → botão **Create Deployment** → branch `main` → commit mais recente
4. Depois **Promote to Production** nesse deploy novo

## Settings → Build and Deployment

- Desligue **Substituições de produção** (aviso amarelo) — use as configurações do projeto
- **Incluir arquivos fora do diretório raiz:** pode ficar habilitado
- Não defina Output Directory (`public` deve estar vazio)

## Variáveis de ambiente (Production)

| Variável | Valor |
|----------|--------|
| `SECRET_KEY` | chave longa aleatória |
| `DEBUG` | `False` |
| `ADMIN_USERNAME` | `admin` (opcional) |
| `ADMIN_EMAIL` | `admin@mydoctor.local` (opcional) |
| `ADMIN_PASSWORD` | senha forte da sua escolha (recomendado em produção) |
| `DATABASE_URL` ou `POSTGRES_URL` | URL do Postgres para dados persistentes (recomendado) |

## Conta admin de teste

Após o deploy, o comando `create_admin` roda automaticamente. **Padrão** (se não definir variáveis):

| Campo | Valor |
|-------|--------|
| Usuário | `admin` |
| E-mail (login do site) | `admin@mydoctor.local` |
| Senha | `Admin@MyDoctor2026` |
| Painel Django | `/admin/` |
| CRM (médico) | `0001` |
| Especialidade | Clínico Geral |

O admin também tem **perfil de médico**: use **Painel Médico** no menu ou **Serviços (Paciente)** para testar as duas áreas.

## Redeploy correto

1. **Deployments** → último deploy da branch `main` (não `6ebc0ed`)
2. **⋯** → **Redeploy** ou **Promote to Production**
3. Nos logs: **Python 3.12**, instalação de pacotes, `collectstatic` (build > ~15s)
4. Abra o domínio: deve carregar a home **My Doctor** com CSS em `/static/`

## Conferir

- Commit recente (não só manifesto Python na raiz)
- Home sem erro 404
- CSS carregando (F12 → Network → `style.css` status 200)

## Páginas do sistema (após login)

| URL | Função |
|-----|--------|
| `/` | Home |
| `/login/` | Login paciente (e-mail) ou médico (CRM) |
| `/register/` | Cadastro |
| `/dashboard/` | Serviços do paciente |
| `/agendar-consulta/` | Agendar |
| `/ver-consultas/` | Listar consultas |
| `/chat/` | Criar/entrar no chat |
| `/minhas-receitas/` | Receitas e atestados |
| `/consultas-gravadas/` | Gravações |
| `/medico/dashboard/` | Painel do médico |
| `/health/` | Status da API |

**Nota:** na Vercel o SQLite fica em `/tmp` (dados podem sumir entre deploys). Para produção persistente, configure `DATABASE_URL` ou `POSTGRES_URL` com um banco Postgres.

## CSS sem estilo (página em branco / links azuis)

O comando `npx plugins add vercel/vercel-plugin` **não** corrige CSS — é só um plugin opcional do Cursor/Vercel.

O problema era a rota `/static/` no `vercel.json` que devolvia 404. A correção usa **WhiteNoise** no Django e envia `/static/` pelo WSGI.
