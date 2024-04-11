import pygame
import concurrent.futures as cf
import time
import numpy as np
from numpy import ndarray

THREAD_DEBUG = False

NUM_THREADS = 8

REAL_RANGE: tuple[float, float] = (-2., 1.)
IMAGINARY_RANGE: tuple[float, float] = (-1., 1.)

WIN_WIDTH: int = 800
WIN_HEIGHT: int = 600
WIN_HEIGHT -= WIN_HEIGHT % NUM_THREADS  # Makes height divisible by the number of threads

MAX_ITER: int = 50
THRESHOLD: float = 2.  # The magnitude where a certain pixel is known to not be a part of the set.

NUM_SHADES: int = 18
COLOR_INTENSITY: int = 175  # Keep at or below 255!

BOX_WIDTH: int = 2  # Cursor drag box border width in pixels.

MIN_SELECTION_SIZE: int = 10  # Minimum number of pixels a selected box can be

class Pixel:
    def __init__(self, color: np.array, x: int, y: int):
        self.color = color
        self.x = x
        self.y = y


def time_checker(func):
    def wrapper(*args):
        start = time.time()
        retval = func(*args)
        print(f'Time elapsed: {(time.time() - start):.4f}s')
        return retval

    return wrapper


def get_iter_val(real_range: tuple[float, float], imaginary_range: list[float, float]) -> int:
    real_len = real_range[1] - real_range[0]
    imaginary_len = imaginary_range[1] - imaginary_range[0]
    window_area = real_len * imaginary_len
    iter_val = 75 + int(1 / window_area) + int(1e-3 / window_area ** 2)
    return iter_val


def clear_cursor_rect(win: pygame.Surface, rect: pygame.Rect, colors: list[tuple[int, int, int]]):
    x_len, y_len = rect.size
    max_win_y = len(colors)
    max_win_x = len(colors[0])
    for h in range(y_len):
        for w in range(x_len):
            if w < BOX_WIDTH or w >= x_len - BOX_WIDTH or h < BOX_WIDTH or h >= y_len - BOX_WIDTH:
                x = rect.left + w
                y = rect.top + h
                if max_win_x > x >= 0 and max_win_y > y >= 0:
                    win.set_at((x, y), colors[y][x])


def print_cursor_rect(win: pygame.Surface, rect: pygame.Rect):
    x_len, y_len = rect.size
    for h in range(y_len):
        for w in range(x_len):
            if w < BOX_WIDTH or w >= x_len - BOX_WIDTH or h < BOX_WIDTH or h >= y_len - BOX_WIDTH:
                win.set_at((rect.left + w, rect.top + h), (255, 255, 255))


def add_pixel_to_array(colors: ndarray, x: int, y: int, win_width: int, win_height: int, max_iter: int,
                       real_range: tuple[float, float], imaginary_range: tuple[float, float]):
    rgb = get_mandel_color(x, y, win_width, win_height, max_iter, real_range, imaginary_range)
    colors[y][x][0] = rgb[0]
    colors[y][x][1] = rgb[1]
    colors[y][x][2] = rgb[2]


@time_checker
def get_all_pixel_colors(win_width: int, win_height: int, num_iter: int, real_range: tuple[float, float],
                         imaginary_range: tuple[float, float]) -> ndarray:

    colors = np.zeros((win_height, win_width, 3), dtype=np.uint8)

    with cf.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:

        total_pixels = win_width * win_height
        ys = [val // win_width for val in range(total_pixels)]
        xs = [val % win_width for val in range(total_pixels)]
        start = time.time()
        pixels = executor.map(get_mandel_color, xs, ys, [win_width] * total_pixels, [win_height] * total_pixels,
                               [num_iter] * total_pixels, [real_range] * total_pixels, [imaginary_range] * total_pixels)
        print(f'{time.time() - start:.4f}')
        for pixel in pixels:
            colors[pixel.y][pixel.x] = pixel.color





    return colors


def get_pixel_complex(x: int, y: int, win_width: int, win_height: int,
                      real_range: tuple[float, float], imaginary_range: tuple[float, float]) -> complex:
    real_range_len = real_range[1] - real_range[0]
    imaginary_range_len = imaginary_range[1] - imaginary_range[0]

    # change in real val with 1 pixel difference in x
    dr: float = real_range_len / win_width
    # change in imaginary val with 1 pixel difference in y
    di: float = imaginary_range_len / win_height

    complex_val: complex = complex(dr * x + real_range[0], di * (win_height - y) + imaginary_range[0])

    return complex_val


def get_mandel_iter_num(c: complex, max_iter: int):
    z: complex = 0 + 0j
    for i in range(max_iter):
        z = z ** 2 + c
        if abs(z) >= THRESHOLD:
            return i
    return -1


def get_mandel_color(x: int, y: int, win_width: int, win_height: int, max_iter: int,
                     real_range: tuple[float, float], imaginary_range: tuple[float, float]) -> Pixel:
    complex_val = get_pixel_complex(x, y, win_width, win_height, real_range, imaginary_range)
    num_iter: int = get_mandel_iter_num(complex_val, max_iter)
    if num_iter == -1:
        return Pixel(np.array([0, 0, 0], dtype=np.uint8), x, y)

    # number of iterations per increase of 1 for each color value (/256)
    dc = COLOR_INTENSITY / NUM_SHADES
    current_shade = num_iter % NUM_SHADES

    current_color_val = int(current_shade * dc)
    red: int = COLOR_INTENSITY - current_color_val
    if current_color_val < (COLOR_INTENSITY + 1) // 2:
        green: int = current_color_val * 2
    else:
        green: int = (COLOR_INTENSITY - current_color_val) * 2
    blue: int = current_color_val
    return Pixel(np.array([red, green, blue], dtype=np.uint8), x, y)


def window_init(win, colors: list[list[tuple[int, int, int]]]):
    win.fill(0)

    rect = pygame.Rect(win.get_rect().center, (0, 0)).inflate(WIN_WIDTH, WIN_HEIGHT)

    for y in range(rect.height):
        for x in range(rect.width):
            color = colors[y][x]
            win.set_at((rect.left + x, rect.top + y), color)


def main():
    pygame.init()
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    real_range = REAL_RANGE
    imaginary_range = IMAGINARY_RANGE
    iter_val = get_iter_val(real_range, imaginary_range)
    old_colors = []
    old_ranges = []
    pixel_colors = get_all_pixel_colors(WIN_WIDTH, WIN_HEIGHT, iter_val, real_range, imaginary_range)
    window_init(window, pixel_colors)

    run = True
    button_down = False
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and len(old_colors) >= 1:
                # Undo
                if event.key == pygame.K_u:
                    pixel_colors = old_colors.pop(-1)
                    real_range, imaginary_range = old_ranges.pop(-1)
                    window_init(window, pixel_colors)

            if not button_down and event.type == pygame.MOUSEBUTTONDOWN:
                button_down = True
                first_pos = pygame.mouse.get_pos()
                cursor_rect = pygame.Rect(first_pos, (0, 0))

            if button_down and event.type == pygame.MOUSEBUTTONUP:
                button_down = False
                old_colors.append(pixel_colors)
                old_ranges.append((real_range, imaginary_range))

                current_x = pygame.mouse.get_pos()[0]
                current_y = pygame.mouse.get_pos()[1]

                x_min = max(min(current_x, first_pos[0]), 0)
                x_max = min(max(current_x, first_pos[0], x_min + MIN_SELECTION_SIZE), window.get_width())
                y_min = max(min(current_y, first_pos[1]), 0)
                y_max = min(max(current_y, first_pos[1], x_min + MIN_SELECTION_SIZE), window.get_height())

                min_val: complex = get_pixel_complex(x_min, y_min, WIN_WIDTH, WIN_HEIGHT, real_range, imaginary_range)
                max_val: complex = get_pixel_complex(x_max, y_max, WIN_WIDTH, WIN_HEIGHT, real_range, imaginary_range)

                real_range = [min_val.real, max_val.real]
                imaginary_range = [max_val.imag, min_val.imag]

                if real_range[0] != real_range[1] and imaginary_range[0] != imaginary_range[1]:
                    iter_val = get_iter_val(real_range, imaginary_range)

                clear_cursor_rect(window, cursor_rect, pixel_colors)

                pixel_colors = get_all_pixel_colors(WIN_WIDTH, WIN_HEIGHT, iter_val, real_range, imaginary_range)
                window_init(window, pixel_colors)

            if button_down and event.type == pygame.MOUSEMOTION:
                current_x = pygame.mouse.get_pos()[0]
                current_y = pygame.mouse.get_pos()[1]
                clear_cursor_rect(window, cursor_rect, pixel_colors)
                x_min = max(min(current_x, first_pos[0]), 0)
                x_max = min(max(current_x, first_pos[0]), window.get_width())
                y_min = max(min(current_y, first_pos[1]), 0)
                y_max = min(max(current_y, first_pos[1]), window.get_height())
                x_len = x_max - x_min
                y_len = y_max - y_min
                cursor_rect = pygame.Rect((x_min, y_min), (x_len, y_len))
                print_cursor_rect(window, cursor_rect)

        pygame.display.flip()

    pygame.quit()
    exit()


if __name__ == '__main__':
    main()
