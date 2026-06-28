"""Testes do ``AsyncBridge`` (jarvis.core.async_bridge).

Roda coroutines a partir de codigo sincrono (worker threads) usando um event
loop reutilizavel por thread. Substitui o ``asyncio.run`` por chamada que existia
no antigo ``Control._run``.
"""

import asyncio

from jarvis.core.async_bridge import AsyncBridge


def test_run_executa_coroutine_e_devolve_resultado():
    bridge = AsyncBridge()

    async def coro():
        return 42

    assert bridge.run(coro()) == 42


def test_run_reutiliza_o_mesmo_loop_na_mesma_thread():
    """Duas chamadas na mesma thread compartilham o loop (threading.local)."""
    bridge = AsyncBridge()

    async def get_loop():
        return asyncio.get_running_loop()

    loop1 = bridge.run(get_loop())
    loop2 = bridge.run(get_loop())
    assert loop1 is loop2
