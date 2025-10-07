#include "camera.h"
#include <opencv2/opencv.hpp>
#include <iostream>

class CameraImpl {
public:
    cv::VideoCapture cap;
    cv::Mat frame;
    bool initialized;
    int index;

    CameraImpl() : initialized(false), index(0) {}
};

Camera::Camera() : pImpl(new CameraImpl()), isInitialized(false), cameraIndex(0) {}

Camera::Camera(int index) : pImpl(new CameraImpl()), isInitialized(false), cameraIndex(index) {
    pImpl->index = index;
}

Camera::~Camera() {
    release();
    delete pImpl;
}

bool Camera::initialize() {
    if (isInitialized) {
        return true;
    }

    pImpl->cap.open(cameraIndex);

    if (!pImpl->cap.isOpened()) {
        std::cerr << "Erro: Nao foi possivel abrir a camera " << cameraIndex << std::endl;
        return false;
    }

    // Configurar propriedades da câmera
    pImpl->cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    pImpl->cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    pImpl->cap.set(cv::CAP_PROP_FPS, 30);

    isInitialized = true;
    pImpl->initialized = true;

    std::cout << "Camera " << cameraIndex << " inicializada com sucesso!" << std::endl;
    return true;
}

bool Camera::isOpened() {
    return isInitialized && pImpl->cap.isOpened();
}

bool Camera::captureFrame() {
    if (!isOpened()) {
        return false;
    }

    bool success = pImpl->cap.read(pImpl->frame);
    if (!success || pImpl->frame.empty()) {
        std::cerr << "Erro: Frame vazio capturado" << std::endl;
        return false;
    }

    return true;
}

void Camera::displayFrame() {
    if (!pImpl->frame.empty()) {
        cv::imshow("Jarvis Camera", pImpl->frame);
    }
}

bool Camera::waitKey(int delay) {
    char key = cv::waitKey(delay);
    return (key == 27 || key == 'q'); // ESC ou 'q' para sair
}

void Camera::release() {
    if (pImpl->cap.isOpened()) {
        pImpl->cap.release();
    }
    cv::destroyAllWindows();
    isInitialized = false;
    pImpl->initialized = false;
    std::cout << "Camera liberada" << std::endl;
}

void Camera::setCameraIndex(int index) {
    cameraIndex = index;
    pImpl->index = index;
}

int Camera::getCameraIndex() const {
    return cameraIndex;
}

cv::Mat Camera::getCurrentFrame() const {
    return pImpl->frame;
}