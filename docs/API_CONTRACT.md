# Contratos das APIs Miyora

## Públicos

### API pública Next.js

- `GET /api/public/info`: informações públicas da fundação.
- `GET /api/public/bot`: estado público do bot. Exige `miyora_session` válido.
- `GET /api/public/guilds`: servidores presentes na sessão do usuário.
- `GET /api/public/guilds/{guildId}/config`: configuração permitida do servidor.
- `PUT /api/public/guilds/{guildId}/config`: atualiza módulos permitidos e idioma.

A sessão usa cookie assinado `miyora_session` com `sub`, `guildIds` e `exp`. Os valores são validados antes de qualquer consulta por guild.

### API administrativa Next.js

Todas as rotas exigem `Authorization: Bearer $OWNER_API_SESSION_SECRET` no painel.

- `GET /api/admin/info`
- `GET /api/admin/guilds`
- `GET /api/admin/members/{guildId}`
- `GET /api/admin/members/search/{memberId}`
- `GET /api/admin/stats`
- `GET /api/admin/economy`
- `POST /api/admin/operations`

## API FastAPI do bot

Todas as chamadas Vercel→Wispbyte exigem `Authorization: Bearer $BOT_API_TOKEN`. Endpoints administrativos exigem `OWNER_API_TOKEN`.

### Ponto de saúde e bot

- `GET /health`
- `GET /api/v1/bot/status`
- `GET /api/v1/guilds`

### Servidores e membros

- `GET /api/v1/guilds/{guildId}/config`
- `PUT /api/v1/guilds/{guildId}/config`
- `GET /api/v1/guilds/{guildId}/members/{memberId}`

### Administração

- `GET /api/v1/admin/info`
- `GET /api/v1/admin/guilds`
- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/economy`
- `GET /api/v1/admin/members/{memberId}`
- `GET /api/v1/admin/members/{memberId}`
- `POST /api/v1/admin/operations`

## Respostas de erro

Respostas HTTP usam JSON. O corpo padrão contém `error` e `code`. Detalhes internos não são enviados ao cliente.

## Variáveis

### API pública

- `PUBLIC_API_SESSION_SECRET`
- `BOT_API_BASE_URL`
- `BOT_API_TOKEN`

### API administrativa

- `OWNER_API_SESSION_SECRET`
- `OWNER_API_TOKEN`
- `BOT_API_BASE_URL`

### Wispbyte

- `DISCORD_BOT_TOKEN`
- `DISCORD_APPLICATION_ID`
- `DATABASE_URL`
- `BOT_API_TOKEN`
- `OWNER_API_TOKEN`
- `BOT_API_HOST`
- `BOT_API_PORT`

`DATABASE_URL` contém a conexão Neon e nunca é exposta ao frontend.
