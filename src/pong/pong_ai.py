from .pong import Pong

predicted_y_global = None


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


def better_agent(pong: Pong, side='left'):
    """
    Returns -1, 0, or +1 for paddle movement.
    -1 = up, +1 = down, 0 = stay
    """
    global predicted_y_global
    side = -1 if side == 'left' else 1

    H = pong.board_size_y
    ball_dx, ball_dy = pong.ball_vx, pong.ball_vy
    ball_x, ball_y = pong.ball_x, pong.ball_y

    if side == 1:
        paddle_y = pong.right_paddle_y
        paddle_x = pong.board_size_x

    else:
        paddle_y = pong.left_paddle_y
        paddle_x = 0

    # ball moving away
    if side * ball_dx < 0:
        predicted_y_global = None
        if paddle_y + pong.paddle_half < H / 2:
            return 1
        elif paddle_y - pong.paddle_half > H / 2:
            return -1
        else:
            return 0

    # ball coming toward us
    else:
        if predicted_y_global is None:
            if ball_dx == 0:
                predicted_y = ball_y
            else:
                steps_to_paddle = abs((paddle_x - ball_x) / ball_dx)
                predicted_y = ball_y
                vy = ball_dy

                for _ in range(int(steps_to_paddle)):
                    predicted_y += vy
                    if predicted_y < 0:
                        predicted_y = -predicted_y
                        vy = -vy
                    elif predicted_y > H:
                        predicted_y = 2 * H - predicted_y
                        vy = -vy
            predicted_y_global = predicted_y

        if abs(paddle_y + pong.ball_size - predicted_y_global) <= pong.paddle_speed:
            return 0
        return 1 if paddle_y < predicted_y_global else -1
