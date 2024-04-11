from mandel import *
def time_test(func, *args):
    start = time.time()
    retval = func(*args)
    return time.time() - start


max_thread_num = 8
running_sums = [0] * max_thread_num
iter_num = 50
for _ in range(iter_num):
    for t in range(1,max_thread_num+1):
        NUM_THREADS = t
        running_sums[t-1] += time_test(get_all_pixel_colors, WIN_WIDTH, WIN_HEIGHT, 50, (1, 2), (-1, 1))
for t in range(1,max_thread_num+1):
    print(f'average time for {t} threads: {running_sums[t-1] / iter_num:.4f}s')

