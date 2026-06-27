import asyncio  # Torna as funções assincronas
from concurrent.futures import ThreadPoolExecutor  # Torna as funções sincronas

import cv2  # Biblioteca que da acessoa câmera

import control  # Importação da classe do Control
import hands  # Importação da classe do Hands

gesture_cooldown = 0


async def main():  # Função de execução principal

    global gesture_cooldown

    hands_task = asyncio.create_task(init_hands())
    control_task = asyncio.create_task(init_control())

    hands_system, control_functions = await asyncio.gather(
        hands_task, control_task
    )  # Criação do objeto Hands e Control

    # Preferencia de camera
    cap = cv2.VideoCapture(0)

    with ThreadPoolExecutor() as executor:  # Torna as funções sincronas
        # Execulta as funçõoes de dentro enquanto a camera está aberta
        while cap.isOpened():
            ret, frame = (
                cap.read()
            )  # Captura de cada frame da camera. Ret é um parametro para verificar a captura

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

                    h, w, _ = (
                        frame.shape
                    )  # Constantes de proporção da camera h = heigth, w = width, _ = canais

                    # (func_exe, func_act, lado_da_mao, cooldown, controla_gravacao)
                    checks = [
                        # Gesto OK -> tirar foto
                        (
                            lambda: executor.submit(
                                control_functions.Capture_Photo, frame, executor
                            ),
                            lambda: hands_system.Map_Ok(h, w, hand_landmarks, frame),
                            "Right",
                            20,
                            False,
                        ),
                        # Gesto Positivo -> iniciar/parar gravacao de video
                        (
                            lambda: executor.submit(control_functions.Capture_Video, cap, executor),
                            lambda: hands_system.Map_Positive(h, w, hand_landmarks, frame),
                            "Left",
                            30,
                            True,
                        ),
                        # Gesto Levantar dedo -> pergunta por voz
                        (
                            lambda: executor.submit(control_functions.Audio_to_Audio, executor),
                            lambda: hands_system.Map_Speak(h, w, hand_landmarks, frame),
                            "Right",
                            20,
                            False,
                        ),
                        # Gesto Faz o L -> foto + pergunta sobre a imagem
                        (
                            lambda: executor.submit(control_functions.Image_Audio, frame, executor),
                            lambda: hands_system.Map_Squid(h, w, hand_landmarks, frame),
                            "Left",
                            20,
                            False,
                        ),
                        # Gesto Rock -> grava video + pergunta sobre o video
                        (
                            lambda: executor.submit(control_functions.Video_Audio, cap, executor),
                            lambda: hands_system.Map_Rock(h, w, hand_landmarks, frame),
                            "Right",
                            20,
                            False,
                        ),
                    ]

                    for func_exe, func_act, side, cooldown, controls_recording in checks:
                        if control_functions.ACTION is False and gesture_cooldown == 0:
                            Check_Gesture(
                                func_exe,
                                func_act,
                                side,
                                hand_label,
                                cooldown,
                                controls_recording,
                                control_functions,
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


# Funcoes da Main!
async def init_hands():  # Função par tornar a iniciação sincrona
    loop = asyncio.get_running_loop()  # Aguarda terminar a funçõao
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, hands.Hands)


async def init_control():  # Função par tornar a iniciação sincrona
    loop = asyncio.get_running_loop()  # Aguarda terminar a funçõao
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, control.Control)


def Check_Gesture(
    func_exe, func_act, side, hand_label, cooldown, controls_recording, control_functions
):
    global gesture_cooldown
    if not (func_act() and hand_label == side):
        return
    gesture_cooldown = cooldown
    if controls_recording:
        # Gestos de video alternam a gravacao; so submete o worker ao INICIAR
        if control_functions.toggle_recording():
            func_exe()
    else:
        func_exe()


# def calculusNormalDistance(X, Y, hand_landmarks):
#   w = 7.87 # 20cm -> 8pl
#   f = 300.154 # Disfoco da camera
#   indicador_5_x = int(hand_landmarks.landmark[5].x * X)
#   mindinho_17_x = int(hand_landmarks.landmark[17].x * X)
#   indicador_5_y = int(hand_landmarks.landmark[5].y * Y)
#   mindinho_17_y = int(hand_landmarks.landmark[17].y * Y)
#   px = mindinho_17_x - indicador_5_x # Largura relativa
#   py = mindinho_17_y - indicador_5_y # Largura relativa
#   if px != 0 and py != 0:
#     Dx = math.sqrt(((w*f)/(px*2))**2)
#     Dy = math.sqrt(((w*f)/(py+1))**2)
#   else:
#     Dx = 150
#     Dy = 150
#   return [Dx*2.54, Dy*2.54]

if __name__ == "__main__":  # Verificação de arquivo principal com prioridade de execução
    asyncio.run(main())  # Execultar a função principal de forma assincrona
