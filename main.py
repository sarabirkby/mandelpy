import pygame
import math
import os

REAL_RANGE = [-2., 1.]
IMAGINARY_RANGE = [-1., 1.]

WIN_WIDTH = 1000
WIN_HEIGHT = 700

WIN_ORIGIN_X = 100
WIN_ORIGIN_Y = 100

MAX_ITER = 50
THRESHOLD = 2.

NUM_SHADES = 5


def get_iter_val(real_range: list[float, float], imaginary_range: list[float, float]) -> int:
    real_len = real_range[1] - real_range[0]
    imaginary_len = imaginary_range[1] - imaginary_range[0]
    iter_val = int(100 / real_len * imaginary_len)
    return iter_val


def clear_cursor_rect(win: pygame.Surface, rect: pygame.Rect, colors: list[tuple[int, int, int]]):
    x_len, y_len = rect.size
    max_win_y = len(colors)
    max_win_x = len(colors[0])
    for h in range(y_len):
        for w in range(x_len):
            if w < 3 or w >= x_len - 3 or h < 3 or h >= y_len - 3:
                x = rect.left + w
                y = rect.top + h
                if max_win_x > x >= 0 and max_win_y > y >= 0:
                    win.set_at((x, y), colors[y][x])


def print_cursor_rect(win: pygame.Surface, rect: pygame.Rect):
    x_len, y_len = rect.size
    for h in range(y_len):
        for w in range(x_len):
            if w < 3 or w >= x_len - 3 or h < 3 or h >= y_len - 3:
                win.set_at((rect.left + w, rect.top + h), (255, 255, 255))


def get_all_pixel_colors(win_width: int, win_height: int, num_iter: int, real_range: tuple[float, float],
                         imaginary_range: tuple[float, float]) -> list[tuple[int, int, int]]:
    colors = []

    for h in range(win_height):
        colors.append([])
        for w in range(win_width):
            colors[h].append(get_mandel_color(w, h, win_width, win_height, num_iter, real_range, imaginary_range))

    return colors


def get_pixel_complex(x: int, y: int, win_width: int, win_height: int,
                      real_range: tuple[float, float], imaginary_range: tuple[float, float]) -> complex:
    real_range_len = real_range[1] - real_range[0]
    imaginary_range_len = imaginary_range[1] - imaginary_range[0]

    # change in real val with 1 pixel difference in x
    dr = real_range_len / win_width
    # change in imaginary val with 1 pixel difference in y
    di = imaginary_range_len / win_height

    complex_val: complex = complex(dr * x + real_range[0], di * (win_height - y) + imaginary_range[0])

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


def window_init(win, colors):
    win.fill(0)

    rect = pygame.Rect(win.get_rect().center, (0, 0)).inflate(WIN_WIDTH, WIN_HEIGHT)

    for y in range(rect.height):
        for x in range(rect.width):
            color = colors[y][x]
            win.set_at((rect.left + x, rect.top + y), color)


def main():
    pygame.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WIN_ORIGIN_X, WIN_ORIGIN_Y)
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    real_range = REAL_RANGE
    imaginary_range = IMAGINARY_RANGE
    iter_val = get_iter_val(real_range, imaginary_range)
    old_colors = []
    pixel_colors = get_all_pixel_colors(WIN_WIDTH, WIN_HEIGHT, iter_val, real_range, imaginary_range)
    window_init(window, pixel_colors)

    run = True
    button_down = False
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and len(old_colors) >= 1:
                if event.key == pygame.K_u:
                    pixel_colors = old_colors[-1]
                    old_colors.pop(len(old_colors)-1)
                    window_init(window, pixel_colors)

            if not button_down and event.type == pygame.MOUSEBUTTONDOWN:
                first_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                cursor_rect = pygame.Rect(first_pos, (0, 0))
                button_down = True

            if button_down and event.type == pygame.MOUSEBUTTONUP:
                old_colors.append(pixel_colors)
                last_pos = pygame.mouse.get_pos()
                max_x = max(last_pos[0], first_pos[0])
                min_x = min(last_pos[0], first_pos[0])
                max_y = max(last_pos[1], first_pos[1])
                min_y = min(last_pos[1], first_pos[1])

                min_val: complex = get_pixel_complex(min_x, min_y, WIN_WIDTH, WIN_HEIGHT, real_range, imaginary_range)
                max_val: complex = get_pixel_complex(max_x, max_y, WIN_WIDTH, WIN_HEIGHT, real_range, imaginary_range)

                real_range = [min_val.real, max_val.real]
                imaginary_range = [max_val.imag, min_val.imag]

                if real_range[0] != real_range[1] and imaginary_range[0] != imaginary_range[1]:
                    iter_val = get_iter_val(real_range, imaginary_range)

                clear_cursor_rect(window, cursor_rect, pixel_colors)

                pixel_colors = get_all_pixel_colors(WIN_WIDTH, WIN_HEIGHT, iter_val, real_range, imaginary_range)
                window_init(window, pixel_colors)

                button_down = False

            if button_down and event.type == pygame.MOUSEMOTION:
                current_x = pygame.mouse.get_pos()[0]
                current_y = pygame.mouse.get_pos()[1]
                clear_cursor_rect(window, cursor_rect, pixel_colors)
                x_min = min((current_x, first_pos[0]))
                x_max = max((current_x, first_pos[0]))
                y_min = min((current_y, first_pos[1]))
                y_max = max((current_y, first_pos[1]))
                x_len = x_max - x_min
                y_len = y_max - y_min
                cursor_rect = pygame.Rect((x_min, y_min), (x_len, y_len))
                print_cursor_rect(window, cursor_rect)
                button_down = True

        pygame.display.flip()

    pygame.quit()
    exit()


if __name__ == '__main__':
    main()

# TODO:
# Add undo button (and redo?)
