"""Shim de compatibilidade: mantem `python main.py` funcionando (README/CLAUDE.md).

O codigo real do loop foi para `jarvis.core.loop` (Onda 5). O entry point
canonico passou a ser `python -m jarvis`; este arquivo apenas redireciona.

Insere `src/` no sys.path para que `python main.py` funcione mesmo sem instalar
o pacote (`pip install -e .`). Quando instalado, o insert e inofensivo.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvis.core.loop import main  # noqa: E402  (depende do sys.path ajustado acima)

if __name__ == "__main__":
    asyncio.run(main())
