# Estado final da integração Miyora

## Funcionando na estrutura

- Supervisor Wispbyte inicia API e bot em `discord-host/main.py`.
- FastAPI expõe saúde, estado do bot, servidores, configuração, membros e administração.
- Vercel publica APIs separadas para site público e painel proprietário.
- OAuth público e proprietário têm estado, callback seguro e cookies HttpOnly.
- Configurações persistem em `guild_configs` no PostgreSQL central.
- Modelos de XP, punições, carteiras locais, banco global, transações, loja, empréstimos, boosters, tickets, sorteios, avaliações e autoroles estão definidos.
- Cogs implementam os comandos básicos de XP, moderação, economia recreativa, tickets, sorteios e avaliações.
- Ajustes econômicos administrativos criam transações e auditoria no banco.

## Não comprovado neste ambiente

- Conexão real ao Neon.
- Login real no Discord.
- Login real do proprietário.
- Execução das migrações em PostgreSQL.
- Sincronização real dos Slash Commands.
- Entrega de mensagens privadas e ações do Discord.
- Integração em produção Vercel/Wispbyte.

## Pendências externas e operacionais

- Configurar tokens OAuth, User ID proprietário, Neon, bot e tokens entre serviços.
- Instalar as dependências em Python 3.12/Linux na Wispbyte.
- Executar `alembic upgrade head` após configurar `DATABASE_URL`.
- Executar migração antes de iniciar os cogs que usam novas tabelas.
- Completar módulos financeiros avançados de loja, empréstimos e boosters conforme credenciais e regras de negócio validadas.
- Testar ações administrativas irreversíveis antes da produção.

## Implantação

### Wispbyte

```bash
cd discord-host
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
alembic upgrade head
python main.py
```

### Vercel

Implante `public-site` e `owner-panel` como dois projetos ou deployments separados. Configure variáveis individuais sem expor segredos ao navegador.
