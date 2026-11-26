from typing import Any


class BotRegistry:
    def __init__(self) -> None:
        self._bot: Any | None = None

    def set(self, bot: Any) -> None:
        self._bot = bot

    def get(self) -> Any | None:
        return self._bot


bot_registry = BotRegistry()
