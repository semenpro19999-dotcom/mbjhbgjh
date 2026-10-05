import cv2

points = []


def mouse_callback(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print("Point selected:", x, y)


def select_area(image_path="screen.png"):
    global points
    points = []

    image = cv2.imread(image_path)

    cv2.namedWindow("Select Minesweeper area")
    cv2.setMouseCallback("Select Minesweeper area", mouse_callback)

    while len(points) < 2:
        cv2.imshow("Select Minesweeper area", image)
        cv2.waitKey(10)

    cv2.destroyAllWindows()

    x1, y1 = points[0]
    x2, y2 = points[1]

    area = (
        min(x1, x2),
        min(y1, y2),
        max(x1, x2),
        max(y1, y2)
    )

    print("Selected area:", area)
    return area
