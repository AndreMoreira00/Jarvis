"""Ponte sync -> async: roda coroutines a partir de worker threads.

Os fluxos rodam em threads do ``ThreadPoolExecutor`` e precisam consumir as
corrotinas do assistente (Jarvis). Antes cada chamada usava ``asyncio.run``, que
criava e destruia um event loop por vez (fragil e custoso). Aqui mantemos um
unico loop reutilizavel por thread (``threading.local``) — a resolucao definitiva
da fronteira async/sync.
"""

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any


class AsyncBridge:
    """Executa uma coroutine ate o fim num event loop reutilizavel por thread."""

    def __init__(self) -> None:
        self._tls = threading.local()

    def run(self, coro: Coroutine[Any, Any, Any]) -> Any:
        loop = getattr(self._tls, "loop", None)
        if loop is None:
            loop = asyncio.new_event_loop()
            self._tls.loop = loop
        return loop.run_until_complete(coro)
