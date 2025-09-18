import time

from pong import Pong
from pong_ai import better_agent


def simple_agent(pong: Pong, side='right'):
    """
    Returns -1, 0, or +1 for paddle movement.
    -1 = up, +1 = down, 0 = stay
    """
    if side == 'right':
        paddle_y = pong.right_paddle_y
    else:
        paddle_y = pong.left_paddle_y

    if paddle_y < pong.ball_y - pong.paddle_speed:
        return +1
    elif paddle_y > pong.ball_y + pong.paddle_speed:
        return -1
    else:
        return 0

def main():
    pong = Pong(board_size_x=20, board_size_y=10, max_score=5, ball_speed=0.7, paddle_speed=0.4, paddle_half=1,
                max_steps=100000)

    running = True
    while running:
        a_left = simple_agent(pong, side='left')
        # a_left = better_agent(pong, side='left')

        # a_right = simple_agent(pong, side='right')
        a_right = better_agent(pong, side='right')

        obs, rewards, done, info = pong.step((a_left, a_right))

        pong.render(scale=40, fps=60)

        if 'score_event' in info:
            if info['score_event'] == 'right':
                pong.serve_after_score(to='left')
            else:
                pong.serve_after_score(to='right')

        if done:
            print("Game finished:", info)
            time.sleep(2)
            pong.reset()

        if not getattr(pong, "_pygame_running", True):
            running = False


if __name__ == "__main__":
    main()
