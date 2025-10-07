#include "camera.h"
#include <iostream>

class CameraSystem {
private:
    Camera* camera;
    bool isRunning;

public:
    CameraSystem() : camera(nullptr), isRunning(false) {}

    ~CameraSystem() {
        stop();
        if (camera) {
            delete camera;
        }
    }

    bool initialize(int cameraIndex = 0) {
        camera = new Camera(cameraIndex);

        if (!camera->initialize()) {
            std::cerr << "Erro ao inicializar camera" << std::endl;
            return false;
        }

        std::cout << "Camera inicializada com sucesso" << std::endl;
        return true;
    }

    void start() {
        if (!camera || !camera->isOpened()) {
            std::cerr << "Camera nao esta inicializada" << std::endl;
            return;
        }

        isRunning = true;
        std::cout << "Iniciando sistema de camera..." << std::endl;
        std::cout << "Pressione 'q' ou ESC para sair" << std::endl;

        runCaptureLoop();
    }

    void stop() {
        isRunning = false;
        if (camera) {
            camera->release();
        }
        std::cout << "Sistema de camera parado" << std::endl;
    }

    bool isSystemRunning() const {
        return isRunning;
    }

private:
    void runCaptureLoop() {
        while (isRunning) {
            if (!camera->captureFrame()) {
                std::cerr << "Erro ao capturar frame" << std::endl;
                break;
            }

            // Exibir frame na janela
            camera->displayFrame();

            // Verificar se o usuário quer sair
            if (camera->waitKey(1)) {
                std::cout << "Finalizando por solicitacao do usuario..." << std::endl;
                isRunning = false;
                break;
            }
        }
    }
};