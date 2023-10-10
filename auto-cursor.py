import pyautogui
import time


def move_mouse_horizontally(speed=0.1):
    """
    Przesuwa myszkę w poziomie z określoną prędkością.

    Parametry:
    - speed: prędkość przesunięcia myszki (im większa wartość, tym wolniejsze przesunięcie)
    """
    try:
        while True:
            current_x, current_y = pyautogui.position()
            pyautogui.moveTo(current_x + 1, current_y, duration=speed)
            time.sleep(speed)
    except KeyboardInterrupt:
        print("Skrypt zakończony")


if __name__ == '__main__':
    move_mouse_horizontally()