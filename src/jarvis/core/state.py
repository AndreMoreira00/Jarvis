"""Estado de runtime compartilhado do subsistema de acoes.

Reune as duas flags efemeras que antes viviam soltas em ``Control`` (a trava
``ACTION`` e o ``threading.Event`` de gravacao). Um unico ``RuntimeState`` e
injetado em ``Capture``, ``Flows`` e no loop, evitando estado duplicado.
"""

import threading


class RuntimeState:
    """Flags efemeras das acoes, compartilhadas entre captura, fluxos e loop."""

    def __init__(self) -> None:
        self._busy = False  # trava global: so uma acao roda por vez
        self._recording = threading.Event()  # gravacao de video (thread-safe)

    @property
    def busy(self) -> bool:
        """True enquanto uma acao esta em curso (impede disparar outra)."""
        return self._busy

    def begin(self) -> None:
        """Marca o sistema como ocupado (inicio de uma acao)."""
        self._busy = True

    def end(self) -> None:
        """Libera o sistema (fim de uma acao)."""
        self._busy = False

    def toggle_recording(self) -> bool:
        """Alterna a gravacao de video. Retorna True se passou a gravar."""
        if self._recording.is_set():
            self._recording.clear()
            return False
        self._recording.set()
        return True

    def start_recording(self) -> None:
        self._recording.set()

    def stop_recording(self) -> None:
        self._recording.clear()

    def is_recording(self) -> bool:
        return self._recording.is_set()
