# Miyora

Monorepo de fundação do projeto Miyora.

## Requisitos

- Python **3.12** em Linux para `discord-host/` e a API FastAPI.
- Node.js 20+ para os dois projetos Next.js.
- PostgreSQL do Neon como banco único centralizado.

O ambiente Android/Termux deste repositório não substitui o runtime de produção da Wispbyte.

## Estrutura

- `public-site/`: Next.js público e API pública em Route Handlers.
- `owner-panel/`: Next.js privado e API administrativa em Route Handlers.
- `discord-host/`: bot Discord com discord.py e API FastAPI.
- `shared/`: contratos e infraestrutura de banco compartilhada.
- `docs/`: documentação técnica.
- `tests/`: verificações básicas do monorepo.

O banco PostgreSQL do Neon é centralizado. Nenhum serviço cria ou mantém banco separado.

## Documentação

- [Estrutura e configuração](docs/PROJECT.md)
- [Comunicação entre serviços](docs/COMMUNICATION.md)
- [Contrato das APIs](docs/API_CONTRACT.md)
- [Dependências](docs/DEPENDENCIES.md)
- [Estado final da integração](docs/FINAL_STATUS.md)
