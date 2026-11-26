# Comunicação entre serviços

## Topologia

- Site público -> API pública: comunicação interna no mesmo deployment Next.js.
- Painel privado -> API administrativa: comunicação interna no mesmo deployment Next.js.
- APIs Next.js -> API do bot: chamadas HTTPS diretas para a URL pública da Wispbyte.
- Discord -> bot: conexão WebSocket/Gateway da biblioteca discord.py.
- Bot e APIs -> Neon: acesso ao único banco PostgreSQL central.

Não existe Cloudflare Tunnel nesta arquitetura. O hostname da Wispbyte deve ser configurado em `BOT_API_BASE_URL` e exposto diretamente.

## Contratos

Os formatos compartilhados ficam em `shared/contracts`. O contrato atual define a resposta mínima de saúde:

```json
{"service":"nome-do-servico","status":"ok"}
```

## APIs implementadas

### API pública Next.js

- `GET /api/health`
- `GET /api/public/info`
- `GET /api/public/bot`
- `GET /api/public/guilds`
- `GET /api/public/guilds/{guildId}/config`
- `PUT /api/public/guilds/{guildId}/config`

### API administrativa Next.js

- `GET /api/admin/info`
- `GET /api/admin/guilds`
- `GET /api/admin/members/{guildId}`
- `GET /api/admin/stats`
- `GET /api/admin/economy`
- `POST /api/admin/operations`

### API FastAPI do bot

- `GET /health`
- `GET /api/v1/bot/status`
- `GET /api/v1/guilds`
- `GET /api/v1/guilds/{guildId}/config`
- `PUT /api/v1/guilds/{guildId}/config`
- `GET /api/v1/guilds/{guildId}/members/{memberId}`
- `GET /api/v1/admin/info`
- `GET /api/v1/admin/guilds`
- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/economy`
- `POST /api/v1/admin/operations`

A API pública usa um cookie de sessão assinado `miyora_session`. A sessão contém `sub`, `guildIds` e `exp` e é criada por uma integração de autenticação futura; o navegador não recebe dados do Neon. O painel usa `OWNER_API_SESSION_SECRET` como segredo Bearer próprio, enquanto a chamada Vercel→Wispbyte usa `OWNER_API_TOKEN` ou `BOT_API_TOKEN`.

## Segurança

Credenciais e tokens são fornecidos por variáveis de ambiente. Chamadas futuras entre Vercel e Wispbyte devem validar `BOT_API_TOKEN`. O painel privado deve manter seus próprios controles de autorização antes de chamar a API administrativa.
