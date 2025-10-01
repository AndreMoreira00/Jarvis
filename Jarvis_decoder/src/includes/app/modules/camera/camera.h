#ifndef CAMERA_H
#define CAMERA_H

class Camera {
private:
    bool isInitialized;
    int cameraIndex;

public:
    Camera();
    Camera(int index);
    Camera();

    bool initialize();
    bool isOpened();
    bool captureFrame();
    void release();

    void setCameraIndex(int index);
    int getCameraIndex() const;
};

#endif // CAMERA_H