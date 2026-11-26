# Estrutura do Miyora

## Responsabilidades

### public-site

Contém o site público e a API pública. Os endpoints ficam em `app/api` como Next.js Route Handlers. O deploy esperado é na Vercel.

### owner-panel

Contém o painel privado e a API administrativa. Os endpoints ficam em `app/api` como Next.js Route Handlers. O deploy esperado é em projeto separado na Vercel.

### discord-host

Contém o bot Discord e a API FastAPI. `main.py` é o processo principal da Wispbyte e supervisiona os dois serviços em uma única execução assíncrona.

### shared

Contém contratos neutros e a configuração compartilhada do banco PostgreSQL. Não contém regras específicas de uma das três aplicações.

### docs

Contém documentação de arquitetura, configuração e operação.

## Tecnologias

- Next.js e TypeScript nos dois sites.
- Python, discord.py e FastAPI no ambiente Discord.
- PostgreSQL hospedado no Neon.
- SQLAlchemy como ORM.
- Alembic para migrações.

## Configuração

1. Copie `.env.example` para `.env` na raiz quando executar processos que leiam variáveis centralizadas.
2. Configure uma URL PostgreSQL válida do Neon em `DATABASE_URL`.
3. Configure o token do Discord em `DISCORD_BOT_TOKEN` somente no ambiente da Wispbyte.
4. Configure `BOT_API_TOKEN` com o mesmo segredo em Vercel e Wispbyte para chamadas autenticadas futuras.
5. Nunca confirme arquivos `.env` ou valores reais.

## Requisitos de runtime

O ambiente Python obrigatório é **Python 3.12** em Linux. A Wispbyte deve instalar `discord-host/requirements.txt` nesse runtime. Python/Android do Termux não representa o ambiente de produção e não deve ser usado como referência de compatibilidade.

## Inicialização local

### Sites Next.js

```bash
npm install
npm run dev:public
npm run dev:owner
```

O painel usa outro terminal ou porta configurada pelo Next.js.

### Discord e API

```bash
cd discord-host
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

A API responde em `/health`. Sem `DISCORD_BOT_TOKEN`, a API continua disponível e o bot permanece desligado.

## OAuth2 administrativo

Configure no projeto `owner-panel` da Vercel:

- `OWNER_DISCORD_CLIENT_ID`: aplicação Discord usada pelo painel privado.
- `OWNER_DISCORD_CLIENT_SECRET`: segredo usado apenas no callback server-side.
- `OWNER_DISCORD_REDIRECT_URI`: URL HTTPS de `/api/auth/discord/callback`.
- `OWNER_DISCORD_USER_ID`: Discord User ID único autorizado a criar sessão administrativa.
- `OWNER_API_SESSION_SECRET`: segredo da sessão HttpOnly do painel.
- `OWNER_API_TOKEN`: token Bearer usado pelo Vercel para chamar FastAPI.

Outro Discord User ID é recusado mesmo que a autenticação OAuth tenha sido concluída.

## OAuth2 público

Configure no projeto `public-site` da Vercel:

- `DISCORD_CLIENT_ID`: ID público da aplicação Discord.
- `DISCORD_CLIENT_SECRET`: segredo usado somente no callback server-side.
- `DISCORD_REDIRECT_URI`: URL HTTPS do callback em produção.
- `DISCORD_INVITE_URL`: convite oficial opcional do bot.
- `PUBLIC_API_SESSION_SECRET`: segredo usado para assinar o cookie da sessão pública.
- `BOT_API_BASE_URL` e `BOT_API_TOKEN`: acesso autenticado à API do bot.

No Discord Developer Portal, autorize a mesma URL HTTPS de `DISCORD_REDIRECT_URI`. O callback solicita `identify guilds`, valida `state`, filtra servidores por Gerenciar Servidor/Administrador e cria uma sessão HttpOnly.

## Migrações

Execute a partir de `discord-host`:

```bash
alembic revision -m "descricao"
alembic upgrade head
```
