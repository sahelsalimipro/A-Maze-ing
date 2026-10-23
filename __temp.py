# This is just a main loop example from Claude, I wanna keep it to analyse and maybe keep ideas for later

# import time

# TARGET_FPS = 12  # terminal redraws don't need 60fps — rain/stars read fine at 8-15
# FRAME_DURATION = 1.0 / TARGET_FPS

# def run(regions: list[Region], screen_w: int, screen_h: int) -> None:
#     last = time.perf_counter()
#     while True:
#         now = time.perf_counter()
#         dt = now - last
#         last = now

#         for region in regions:
#             region.update(dt)          # advance animation state

#         screen = composite(screen_w, screen_h, regions)
#         draw(screen)                    # print it

#         elapsed = time.perf_counter() - now
#         sleep_time = FRAME_DURATION - elapsed
#         if sleep_time > 0:
#             time.sleep(sleep_time)
