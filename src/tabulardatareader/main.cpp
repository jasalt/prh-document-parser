#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

int main(int argc, char* args[])
{
    using namespace cv;

    if (argc < 2)
    {
        std::cout << "error: too few parameters." << std::endl;
        return -1;
    }

    std::string win_title = "Tabular data reader";
    bool autosize = false;

    Mat original_img, gray_img, threshed;

    // Read image and threshold it just in case.
    std::string path = std::string(args[1]);
    original_img = imread(path, 1);
    cvtColor(original_img, gray_img, CV_BGR2GRAY);
    adaptiveThreshold(gray_img, threshed, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY_INV, 21, 2);

    // Blur the image horizontally to make the letters overlap a bit.
    blur(threshed, threshed, Size(30, 1));

    vector<vector<Point> > contours;
    vector<Vec4i> hierachy;
    vector<Rect> rects;

    // Find contours and calculate approximate bounding rectangles.
    findContours(threshed, contours, hierachy, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE, Point(-1, -1));
    vector<vector<Point> > contours_poly(contours.size());
    for (size_t i=0; i<contours.size(); i++)
    {
        approxPolyDP(Mat(contours[i]), contours_poly[i], 3, true);
        if (contourArea(Mat(contours[i])) > 20)
        {
            Rect rect = boundingRect(Mat(contours_poly[i]));
            if (rect.height > 20.0f)
            {
                rect.width += 2;
                rect.height += 2;
                rects.push_back(rect);

                // Draw blue rectangles to the original image for debugging purposes.
                rectangle(original_img, rect.tl(), rect.br(), Scalar(200, 100, 100), 5, 8, 0);
            }
        }
    }

    // Open a window and display the image.
    namedWindow(win_title, autosize ? CV_WINDOW_AUTOSIZE : CV_WINDOW_NORMAL);
    imshow(win_title, original_img);
    waitKey(0);

    return 0;
}
