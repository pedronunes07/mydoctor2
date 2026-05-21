# My Doctor — Revisão do sistema

## O que já funciona

| Módulo | Status | Observação |
|--------|--------|------------|
| Home, login, cadastro | OK | Paciente (e-mail) e médico (CRM) |
| Admin Django `/admin/` | OK | Conta `admin` com perfil médico |
| Agendar consulta | OK | Especialidades alinhadas ao cadastro médico |
| Ver consultas (paciente) | OK | Lista + entrar na ligação |
| Painel médico | OK | Pendentes + assumir + minhas consultas |
| Sala de chat + texto | OK | Mensagens em tempo real (polling) |
| Videochamada WebRTC | OK | STUN Google; um inicia, outro aceita |
| Gravações | Corrigido | Salvas no banco (`file_blob` na Vercel) |
| Receitas / atestados | OK | Médico emite, paciente vê em Minhas receitas |
| CSS / estáticos | OK | WhiteNoise na Vercel |

## Fluxo recomendado de teste

1. **Paciente:** cadastro → agendar (Clínico Geral) → Ver consultas → Entrar na ligação  
2. **Médico:** login → Painel médico → Assumir consulta → Entrar na ligação  
3. **Médico:** Iniciar vídeo  
4. **Paciente:** Aceitar vídeo  
5. **Qualquer um:** Gravar → falar alguns segundos → Parar gravação  
6. **Consultas gravadas** (`/consultas-gravadas/`) — reproduzir o vídeo  

## O que foi corrigido agora (gravações)

- Upload com `credentials: 'same-origin'` e mensagens de erro claras  
- Gravação mistura áudio/vídeo local + remoto  
- Duração enviada ao servidor  
- Na **Vercel**, arquivo guardado em **`file_blob`** no SQLite (não só pasta `/tmp/media`)  
- Reprodução via `/gravacao/<id>/` (não depende de URL de media efêmera)  
- Ao encerrar chamada, gravação em andamento é enviada antes de sair  

## Limitações importantes (Vercel)

| Item | Impacto |
|------|---------|
| SQLite em `/tmp` | Cadastros e gravações **podem sumir** após redeploy ou instância fria |
| Tamanho do upload | Máx. ~45 MB por gravação (limite da função serverless) |
| WebRTC | Precisa HTTPS + permissão câmera/mic; NAT muito restrito pode falhar |
| Gravação automática | Não grava sozinha — é preciso clicar **Gravar** |

### Produção de verdade (próximos passos)

1. **Vercel Postgres** ou Neon — banco persistente  
2. **Vercel Blob** ou S3 — arquivos de gravação grandes e permanentes  
3. **TURN server** — ligações mais estáveis que só STUN  
4. **Domínio fixo** + `CSRF_TRUSTED_ORIGINS`  

## Pendências / melhorias desejáveis

- [ ] Notificação por e-mail ao agendar / assumir consulta  
- [ ] Calendário e lembretes de consulta  
- [ ] Gravação automática opcional ao iniciar a chamada  
- [ ] Histórico de ligações (log sem vídeo) mesmo sem gravar  
- [ ] App Expo (`mydoctor/`) apontando para API em produção  
- [ ] Testes automatizados  
- [ ] Páginas Planos / Segurança (hoje são âncoras na home)  
- [ ] Pagamento / planos premium (botão ainda é placeholder)  

## Variáveis de ambiente (Vercel)

| Variável | Uso |
|----------|-----|
| `SECRET_KEY` | Django |
| `DEBUG` | `False` em produção |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` | Conta de teste |
| `ADMIN_CRM` | CRM do admin como médico (`ADMIN-0001`) |

## Comandos úteis

```bash
cd mydoctor-api
python manage.py migrate
python manage.py create_admin --force
python manage.py runserver
```

Deploy: Root Directory = `mydoctor-api`, commit recente na `main`.
