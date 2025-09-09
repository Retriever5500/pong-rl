import time

from pong import Pong
from agent import better_agent

def simple_agent(ball_y, paddle_y, paddle_speed):
    """
    Returns -1, 0, or +1 for paddle movement.
    -1 = up, +1 = down, 0 = stay
    """
    if paddle_y < ball_y - paddle_speed:
        return +1
    elif paddle_y > ball_y + paddle_speed:
        return -1
    else:
        return 0


def main():
    time_left = []
    time_right = []
    pong = Pong(board_size_x=20, board_size_y=10, max_score=5, ball_speed=0.6, paddle_speed=0.4, paddle_half=1,
                max_steps=100000)

    running = True
    while running:
        start_time = time.time()
        a_left = better_agent(pong)
        time_left.append(time.time()-start_time)

        start_time = time.time()
        a_right = simple_agent(pong.ball_y, pong.right_paddle_y, pong.paddle_speed)
        time_right.append(time.time() - start_time)

        obs, rewards, done, info = pong.step((a_left, a_right))

        pong.render(scale=40, fps=60)

        if done:
            print("Game finished:", info)
            time.sleep(2)
            print(sum(time_left)/len(time_left),sum(time_right)/len(time_right))
            pong.reset()

        if not getattr(pong, "_pygame_running", True):
            running = False


if __name__ == "__main__":
    main()
