"""Classificacao pura de gestos a partir dos landmarks do MediaPipe Hands.

Funcoes sem efeito colateral: recebem ``(h, w, hand_landmarks)`` e devolvem
``bool``. ``hand_landmarks`` so precisa expor ``.landmark[i].x`` e ``.y``
(coordenadas normalizadas em [0, 1]), entao funcionam com o objeto real do
MediaPipe ou com qualquer fake equivalente (ver testes).

A conversao para pixel usa ``int(norm * w|h)`` e os limites escalam com a
resolucao (ex.: ``0.05 * w``), de modo que o reconhecimento independe do tamanho
do frame entregue pela camera.
"""

import math
from collections.abc import Sequence
from typing import Protocol

# Indices dos landmarks do MediaPipe Hands usados na classificacao.
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
RING_MCP = 13
RING_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_TIP = 20

# Margem (fracao de h/w) que um dedo precisa ultrapassar para contar como "erguido".
RAISED_MARGIN = 0.05


class Landmark(Protocol):
    """Ponto normalizado: x e y em [0, 1] (z e ignorado pela classificacao)."""

    x: float
    y: float


class HandLandmarks(Protocol):
    """Mao detectada: lista indexavel de 21 landmarks."""

    landmark: Sequence[Landmark]


def _x(hand: HandLandmarks, idx: int, w: int) -> int:
    """Coordenada x do landmark ``idx`` em pixels."""
    return int(hand.landmark[idx].x * w)


def _y(hand: HandLandmarks, idx: int, h: int) -> int:
    """Coordenada y do landmark ``idx`` em pixels (cresce para baixo)."""
    return int(hand.landmark[idx].y * h)


def distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """Distancia euclidiana entre dois pontos (x, y)."""
    return math.hypot(point1[0] - point2[0], point1[1] - point2[1])


def is_ok(h: int, w: int, hand: HandLandmarks) -> bool:
    """Gesto OK: ponta do polegar encosta na do indicador, demais dedos abaixados."""
    thumb_tip = (_x(hand, THUMB_TIP, w), _y(hand, THUMB_TIP, h))
    index_tip = (_x(hand, INDEX_TIP, w), _y(hand, INDEX_TIP, h))
    return (
        distance(thumb_tip, index_tip) < RAISED_MARGIN * w
        and _y(hand, INDEX_MCP, h) > _y(hand, INDEX_PIP, h)
        and _y(hand, THUMB_CMC, h) > _y(hand, INDEX_PIP, h)
        and _x(hand, THUMB_IP, w) > _x(hand, INDEX_MCP, w)
    )


def is_positive(h: int, w: int, hand: HandLandmarks) -> bool:
    """Joinha: polegar erguido bem acima da base, os outros quatro dedos dobrados."""
    return (
        _y(hand, THUMB_TIP, h) < _y(hand, THUMB_CMC, h) - RAISED_MARGIN * h
        and _y(hand, INDEX_TIP, h) > _y(hand, INDEX_MCP, h)
        and _y(hand, MIDDLE_TIP, h) > _y(hand, MIDDLE_MCP, h)
        and _y(hand, RING_TIP, h) > _y(hand, RING_MCP, h)
        and _y(hand, PINKY_TIP, h) > _y(hand, PINKY_MCP, h)
    )


def is_speak(h: int, w: int, hand: HandLandmarks) -> bool:
    """Indicador erguido, polegar deslocado para a direita, demais dedos dobrados."""
    return (
        _y(hand, INDEX_TIP, h) < _y(hand, INDEX_MCP, h) - RAISED_MARGIN * h
        and _x(hand, THUMB_TIP, w) > _x(hand, THUMB_CMC, w)
        and _y(hand, MIDDLE_TIP, h) > _y(hand, MIDDLE_MCP, h)
        and _y(hand, RING_TIP, h) > _y(hand, RING_MCP, h)
        and _y(hand, PINKY_TIP, h) > _y(hand, PINKY_MCP, h)
    )


def is_squid(h: int, w: int, hand: HandLandmarks) -> bool:
    """'L': indicador erguido e polegar aberto para a esquerda, demais dedos dobrados."""
    return (
        _y(hand, INDEX_TIP, h) < _y(hand, INDEX_PIP, h) - RAISED_MARGIN * h
        and _x(hand, THUMB_TIP, w) < _x(hand, THUMB_MCP, w)
        and _y(hand, PINKY_TIP, h) > _y(hand, PINKY_MCP, h)
        and _y(hand, MIDDLE_TIP, h) > _y(hand, MIDDLE_MCP, h)
        and _y(hand, RING_TIP, h) > _y(hand, RING_MCP, h)
    )


def is_rock(h: int, w: int, hand: HandLandmarks) -> bool:
    """Rock: indicador e mindinho erguidos, medio e anelar dobrados."""
    return (
        _y(hand, INDEX_TIP, h) < _y(hand, INDEX_PIP, h) - RAISED_MARGIN * h
        and _y(hand, PINKY_TIP, h) < _y(hand, PINKY_PIP, h) - RAISED_MARGIN * h
        and _y(hand, MIDDLE_TIP, h) > _y(hand, MIDDLE_MCP, h)
        and _y(hand, RING_TIP, h) > _y(hand, RING_MCP, h)
    )
