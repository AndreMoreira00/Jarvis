#ifndef CAMERA_H
#define CAMERA_H

#include <opencv2/opencv.hpp>

class CameraImpl; // Forward declaration

class Camera {
private:
    CameraImpl* pImpl; // Pimpl idiom para esconder dependências do OpenCV
    bool isInitialized;
    int cameraIndex;

public:
    Camera();
    Camera(int index);
    ~Camera();

    bool initialize();
    bool isOpened();
    bool captureFrame();
    void displayFrame();
    bool waitKey(int delay = 1);
    void release();

    void setCameraIndex(int index);
    int getCameraIndex() const;
    cv::Mat getCurrentFrame() const;
};

#endif // CAMERA_H