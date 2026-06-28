"""Smoke test da fundacao de testes.

Valida que o mock total funciona: todos os modulos de producao importam sem as
libs pesadas instaladas, e que as fixtures canonicas de gesto disparam o Map_*
correto. Se este arquivo falhar, a infra (conftest) esta quebrada e nenhum outro
teste e confiavel.
"""

import importlib

import conftest
import pytest


def test_modulos_de_producao_importam_sem_libs_pesadas():
    # Se algum stub estiver faltando, o import explode aqui.
    for nome in [
        "jarvis.config",
        "jarvis.vision.hands",
        "jarvis.core.state",
        "jarvis.core.async_bridge",
        "jarvis.core.capture",
        "jarvis.core.flows",
        "jarvis.core.loop",
        "jarvis.services.jarvis",
        "jarvis.services.manager",
        "jarvis.app",
        "bootstrap",
    ]:
        mod = importlib.import_module(nome)
        assert mod is not None


def test_construtor_de_landmarks_tem_21_pontos():
    lm = conftest.make_hand_landmarks()
    assert len(lm.landmark) == 21
    assert all(hasattr(p, "x") and hasattr(p, "y") for p in lm.landmark)


@pytest.mark.parametrize("nome_map,coords", list(conftest.ALL_GESTURES.items()))
def test_fixture_canonica_dispara_seu_gesto(
    nome_map, coords, hands_instance, frame_size, fake_frame
):
    h, w = frame_size
    lm = conftest.make_hand_landmarks(coords)
    assert getattr(hands_instance, nome_map)(h, w, lm, fake_frame) is True


def test_pose_neutra_nao_dispara_nenhum_gesto(hands_instance, frame_size, fake_frame):
    h, w = frame_size
    lm = conftest.make_hand_landmarks(conftest.GESTURE_NONE)
    for nome_map in conftest.ALL_GESTURES:
        assert not getattr(hands_instance, nome_map)(h, w, lm, fake_frame)
