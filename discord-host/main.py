import asyncio
import logging
import os
import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from app.config import settings

if settings.database_url:
    os.environ["DATABASE_URL"] = settings.database_url

from app.main import app
from bot.core.bot import MiyoraBot
from bot.services.database import DatabaseService
from app.bot_registry import bot_registry

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("miyora")


async def run_api() -> None:
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=settings.bot_api_host,
            port=settings.bot_api_port,
            log_level="info",
        )
    )
    await server.serve()


async def run_discord_bot() -> None:
    while True:
        bot = MiyoraBot()
        bot_registry.set(bot)
        try:
            await bot.start(settings.discord_bot_token, reconnect=True)
            return
        except asyncio.CancelledError:
            await bot.close()
            raise
        except Exception:
            log.exception("O bot Miyora terminou com erro; reiniciando em 5 segundos")
            await bot.close()
            await asyncio.sleep(5)


async def supervise() -> None:
    tasks = [asyncio.create_task(run_api(), name="miyora-api")]

    if settings.discord_bot_token:
        tasks.append(asyncio.create_task(run_discord_bot(), name="miyora-bot"))
    else:
        log.warning("DISCORD_BOT_TOKEN não configurado; o bot permanece desligado")

    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task.cancelled():
                continue
            exception = task.exception()
            if exception:
                log.error("Serviço finalizado com erro: %s", exception)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    finally:
        DatabaseService.close()


if __name__ == "__main__":
    asyncio.run(supervise())
