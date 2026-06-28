import asyncio  # Torna as funções assincronas
from concurrent.futures import ThreadPoolExecutor  # Torna as funções sincronas

import cv2  # Biblioteca que da acessoa câmera

from jarvis.app import build  # Composition root: monta hands/capture/flows/state

gesture_cooldown = 0


async def main():  # Função de execução principal
    global gesture_cooldown

    # Monta o grafo de objetos (composition root) fora do event loop da camera.
    app = await asyncio.get_running_loop().run_in_executor(None, build)
    hands_system = app.hands
    capture = app.capture
    flows = app.flows
    state = app.state

    # Preferencia de camera
    cap = cv2.VideoCapture(0)

    with ThreadPoolExecutor() as executor:  # Torna as funções sincronas
        # Execulta as funçõoes de dentro enquanto a camera está aberta
        while cap.isOpened():
            ret, frame = cap.read()  # Captura de cada frame; ret indica sucesso

            if not ret:
                print("Erro ao capturar o frame.")
                break

            rgb_frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )  # Configuração de cores para a identificação das mãos
            results = hands_system.hands.process(rgb_frame)  # Resposta da identificação das mãos

            if (
                results.multi_hand_landmarks and results.multi_handedness
            ):  # Marcaçãos dos pontos e retas nas mãos
                for hand_landmarks, hand_handedness in zip(
                    results.multi_hand_landmarks, results.multi_handedness, strict=True
                ):  # Obtemos as previsões em tempo real dos pontos e das retas
                    hand_label = hand_handedness.classification[
                        0
                    ].label  # Identificação da mão direita e esquerda

                    h, w, _ = frame.shape  # Proporção da camera (h=altura, w=largura)

                    # (func_exe, func_act, lado_da_mao, cooldown, controla_gravacao)
                    checks = [
                        # Gesto OK -> tirar foto
                        (
                            lambda: executor.submit(capture.capture_photo, frame, executor),
                            lambda: hands_system.map_ok(h, w, hand_landmarks, frame),
                            "Right",
                            20,
                            False,
                        ),
                        # Gesto Positivo -> iniciar/parar gravacao de video
                        (
                            lambda: executor.submit(capture.capture_video, cap, executor),
                            lambda: hands_system.map_positive(h, w, hand_landmarks, frame),
                            "Left",
                            30,
                            True,
                        ),
                        # Gesto Levantar dedo -> pergunta por voz
                        (
                            lambda: executor.submit(flows.audio_to_audio, executor),
                            lambda: hands_system.map_speak(h, w, hand_landmarks, frame),
                            "Right",
                            20,
                            False,
                        ),
                        # Gesto Faz o L -> foto + pergunta sobre a imagem
                        (
                            lambda: executor.submit(flows.image_audio, frame, executor),
                            lambda: hands_system.map_squid(h, w, hand_landmarks, frame),
                            "Left",
                            20,
                            False,
                        ),
                        # Gesto Rock -> grava video + pergunta sobre o video
                        (
                            lambda: executor.submit(flows.video_audio, cap, executor),
                            lambda: hands_system.map_rock(h, w, hand_landmarks, frame),
                            "Right",
                            20,
                            False,
                        ),
                    ]

                    for func_exe, func_act, side, cooldown, controls_recording in checks:
                        if state.busy is False and gesture_cooldown == 0:
                            check_gesture(
                                func_exe,
                                func_act,
                                side,
                                hand_label,
                                cooldown,
                                controls_recording,
                                state,
                            )

                    # Reduz o cooldown a cada frame
                    if gesture_cooldown > 0:
                        gesture_cooldown -= 1

                    hands_system.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, hands_system.mp_hands.HAND_CONNECTIONS
                    )  # Reenderizar os pontos e retas na tela

            cv2.imshow("MediaPipe Hands", frame)  # Criar uam tela com a visao da camera

            if cv2.waitKey(1) & 0xFF == ord("q"):  # Encerra o programa clicando Q
                break

        cap.release()  # Fecha a camera
        cv2.destroyAllWindows()  # Destroi a tela da camera


def check_gesture(func_exe, func_act, side, hand_label, cooldown, controls_recording, state):
    global gesture_cooldown
    if not (func_act() and hand_label == side):
        return
    gesture_cooldown = cooldown
    if controls_recording:
        # Gestos de video alternam a gravacao; so submete o worker ao INICIAR
        if state.toggle_recording():
            func_exe()
    else:
        func_exe()


# Entry point: o disparo de `asyncio.run(main())` vive em jarvis/__main__.py
# (`python -m jarvis`) e no shim main.py da raiz (`python main.py`).
