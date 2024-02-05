import pygame
import math

REAL_RANGE = (-2., 1.)
IMAGINARY_RANGE = (-1., 1.)

WIN_WIDTH = 1000
WIN_HEIGHT = 700

MAX_ITER = 100
THRESHOLD = 2.

NUM_SHADES = 5


def get_pixel_complex(x: int, y:int, win_width: int, win_height: int, real_range: tuple[float, float], imaginary_range: tuple[float, float]) -> complex:
    real_range_len = real_range[1] - real_range[0]
    imaginary_range_len = imaginary_range[1] - imaginary_range[0]

    # change in real val with 1 pixel difference in x
    dr = real_range_len / win_width
    # change in imaginary val with 1 pixel difference in y
    di = imaginary_range_len / win_height

    complex_val: complex = complex(dr * x + real_range[0], di * (win_height-y) + imaginary_range[0])

    return complex_val

def get_mandel_iter_num(c: complex, max_iter: int):
    z = 0 + 0j
    for i in range(max_iter):
        z = z ** 2 + c
        if abs(z) >= THRESHOLD:
            return i
    return -1


def get_mandel_color(x: int, y: int, win_width: int, win_height: int, max_iter: int,
                     real_range: tuple[float, float], imaginary_range: tuple[float, float]) -> tuple[int, int, int]:
    # one pixel of change in real

    complex_val = get_pixel_complex(x, y, win_width, win_height, real_range, imaginary_range)
    num_iter: int = get_mandel_iter_num(complex_val, max_iter)
    if num_iter == -1:
        return 0, 0, 0

    # number of iterations per increase of 1 for each color value (/256)
    dr = 255 / (NUM_SHADES ** 3)
    dg = 255 / (NUM_SHADES ** 2)
    db = 255 / NUM_SHADES

    red: int = int((num_iter % NUM_SHADES ** 3) * dr)
    green: int = int((num_iter % NUM_SHADES ** 2) * dg)
    blue: int = int((num_iter % NUM_SHADES) * db)

    return red, green, blue




def window_init(win):
    win.fill(0)

    rect = pygame.Rect(win.get_rect().center, (0, 0)).inflate(WIN_WIDTH, WIN_HEIGHT)

    for y in range(rect.height):
        for x in range(rect.width):
            color = get_mandel_color(x, y, WIN_WIDTH, WIN_HEIGHT, MAX_ITER, REAL_RANGE, IMAGINARY_RANGE)
            win.set_at((rect.left + x, rect.top + y), color)

pygame.init()
window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
window_init(window)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()
exit()