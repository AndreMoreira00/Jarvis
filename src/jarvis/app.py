"""Composition root: monta e conecta o grafo de objetos do Jarvis.

Le a ``Config``, inicializa o mixer e injeta os colaboradores em cadeia. Mantem
todo o 'wiring' num so lugar, fora das classes de dominio (que recebem suas
dependencias por construtor). Substitui o antigo construtor god-class de
``Control``, que criava tudo dentro de si.
"""

from dataclasses import dataclass

from pygame import mixer

from jarvis.config import Config
from jarvis.core.async_bridge import AsyncBridge
from jarvis.core.capture import Capture
from jarvis.core.flows import Flows
from jarvis.core.state import RuntimeState
from jarvis.services.jarvis import Jarvis
from jarvis.services.manager import Manager
from jarvis.vision.hands import Hands


@dataclass
class App:
    """Componentes montados que o loop principal consome."""

    hands: Hands
    capture: Capture
    flows: Flows
    state: RuntimeState


def build() -> App:
    """Constroi e conecta todos os subsistemas (composition root)."""
    config = Config.from_env()
    mixer.init()  # Servico de audio do pygame

    state = RuntimeState()
    bridge = AsyncBridge()
    uploader = Manager(config)
    assistant = Jarvis(mixer, config)
    capture = Capture(config, uploader, state, mixer)
    flows = Flows(capture, assistant, bridge, state)
    hands = Hands()

    return App(hands=hands, capture=capture, flows=flows, state=state)
