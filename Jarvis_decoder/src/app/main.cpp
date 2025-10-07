#include <iostream>
#include "modules/camera/camera_system.cpp"

int main() {
    std::cout << "Inicializando sistema Jarvis..." << std::endl;

    // Inicializar sistema de camera
    CameraSystem cameraSystem;

    if (!cameraSystem.initialize()) {
        std::cerr << "Falha ao inicializar sistema de camera" << std::endl;
        return -1;
    }else{
        std::cout << "Sistema de camera inicializado com sucesso" << std::endl;
    }

    std::cout << "Sistema Jarvis inicializado com sucesso!" << std::endl;
    std::cout << "Iniciando loop principal..." << std::endl;

    // Iniciar captura e visualização da câmera
    cameraSystem.start();

    // TODO: Inicializar sistema de hands
    // TODO: Inicializar sistema de controle

    std::cout << "Sistema Jarvis finalizado." << std::endl;
    return 0;
}