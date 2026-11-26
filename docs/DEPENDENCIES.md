# Dependências da fundação

## Frontend

Os workspaces `public-site` e `owner-panel` usam Next.js 15, React 19 e TypeScript 5.

## Backend Discord

Runtime obrigatório: **Python 3.12 em Linux**. `discord-host/requirements.txt` inclui:

- `discord.py`: gateway e Slash Commands.
- `FastAPI` e `Uvicorn`: API HTTP assíncrona.
- `SQLAlchemy`: ORM da única conexão PostgreSQL.
- `Alembic`: migrações do banco central.
- `psycopg[binary]`: driver PostgreSQL com wheel nativo disponível em Linux/Python 3.12.
- `pydantic-settings`: leitura tipada das variáveis de ambiente.

O extra `standard` do Uvicorn habilita recursos adicionais suportados pelo Linux de produção. Não usar a limitação Android/Termux como parâmetro para alterar essas dependências.

## Banco

A configuração central usa SQLAlchemy. O Neon deve fornecer uma URL PostgreSQL com SSL. Não há segunda conexão de banco, cache persistente ou banco local nesta fundação.
