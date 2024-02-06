#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <chrono>
double prev_frame_time = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count() / 1000.0;
double new_frame_time, fps;

int main() {
    cv::VideoCapture video(0);
    if (!video.isOpened()) {
        return -1;
    }
    cv::Mat frame, gray;
    cv::QRCodeDetector detector;

    int frameWidth = video.get(cv::CAP_PROP_FRAME_WIDTH);
    int frameHeight = video.get(cv::CAP_PROP_FRAME_HEIGHT);

    int count = 0;
    cv::TickMeter tm;

    while (video.read(frame)) {
      cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

        std::vector<cv::Point> corners;
        std::string data = detector.detectAndDecode(gray, corners);

        if (!data.empty())
        {
            std::cout << "QR Code detected with data: " << data << std::endl;

            // Draw the detected QR code
            cv::polylines(frame, corners, true, cv::Scalar(0, 255, 0), 2);
        }
        // Inside the loop where you process each frame:
        new_frame_time = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count() / 1000.0;

        // Calculating the fps
        fps = 1 / (new_frame_time - prev_frame_time);
        prev_frame_time = new_frame_time;

        // Converting the fps to string so that we can display it on frame
        std::string fps_str = std::to_string(static_cast<int>(fps));
        cv::putText(frame, "FPS: " + std::to_string(fps), cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255, 255, 255), 2);
        cv::imshow("Video Feed", frame);

        if (cv::waitKey(25) >= 0) {
            break;
        }
    }

    video.release();
    cv::destroyAllWindows();
    return 0;
}
