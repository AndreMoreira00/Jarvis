"""Entry point canonico: ``python -m jarvis``.

Dispara o loop principal da camera (jarvis.core.loop.main) no asyncio.
"""

import asyncio

from jarvis.core.loop import main

if __name__ == "__main__":
    asyncio.run(main())
