import cv2
import numpy as np

points = []


def mouse_callback(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"  📍 Point {len(points)}: ({x}, {y})")


def select_area(image_source=None):
    """
    Позволяет выбрать область игры на скриншоте.
    
    image_source: путь к файлу или None для автоскриншота.
    Возвращает (x1, y1, x2, y2).
    """
    global points
    points = []

    if image_source and isinstance(image_source, str):
        image = cv2.imread(image_source)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_source}")
    else:
        # Делаем скриншот
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise RuntimeError(f"Cannot take screenshot: {e}")

    window_name = "Select Minesweeper area (click 2 corners, then press ENTER)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("  🖱️ Click 2 corners of the Minesweeper board, then press ENTER")

    while True:
        display = image.copy()

        # Рисуем точки
        for i, (px, py) in enumerate(points):
            cv2.circle(display, (px, py), 8, (0, 255, 0), -1)
            cv2.putText(display, str(i+1), (px + 10, py - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Если 2 точки — рисуем прямоугольник
        if len(points) >= 2:
            cv2.rectangle(display, points[0], points[1], (0, 255, 0), 3)

        cv2.imshow(window_name, display)
        key = cv2.waitKey(50) & 0xFF

        if key == 13 and len(points) >= 2:  # ENTER
            break
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            raise KeyboardInterrupt("Selection cancelled")

    cv2.destroyAllWindows()

    x1, y1 = points[0]
    x2, y2 = points[1]

    area = (
        min(x1, x2),
        min(y1, y2),
        max(x1, x2),
        max(y1, y2)
    )

    print(f"  ✅ Selected area: {area}")
    print(f"  📐 Size: {area[2]-area[0]}x{area[3]-area[1]} px")
    return area
