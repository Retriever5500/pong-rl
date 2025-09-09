import numpy as np
import pygame
import time

class Point:
    def __int__(self, x, y, v_x=0, v_y=0):
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y

    def move(self):
        self.x += self.v_x
        self.y += self.v_y

    def __eq__(self, other):
        if type(self) != type(other):
            raise TypeError()
        if self.x == other.x and self.y == other.y:
            return True
        return False


class Pong:
    def __init__(
            self,
            board_size_x=20,
            board_size_y=10,
            paddle_half=0.1,
            paddle_speed=0.04,
            ball_speed=0.03,
            max_score=1,
            max_steps=1000,
            seed=None,
            ball_speed_variation=0.005
    ):
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.paddle_half = float(paddle_half)
        self.paddle_speed = float(paddle_speed)
        self.ball_speed = float(ball_speed)
        self.max_score = int(max_score)
        self.max_steps = int(max_steps)
        self.ball_speed_variation = float(ball_speed_variation)

        self.rng = np.random.RandomState(seed)

        self.left_paddle_y = None
        self.right_paddle_y = None
        self.ball_x = None
        self.ball_y = None
        self.ball_vx = None
        self.ball_vy = None
        self.left_score = 0
        self.right_score = 0
        self.steps = 0
        self.done = False

        self.reset()

    def reset(self, serve_to=None):
        self.left_paddle_y = self.board_size_y / 2
        self.right_paddle_y = self.board_size_y / 2
        self.left_score = 0
        self.right_score = 0
        self.steps = 0
        self.done = False

        self.ball_x = self.board_size_x / 2
        self.ball_y = self.board_size_y / 2

        if serve_to is None:
            side = self.rng.choice(['left', 'right'])
        else:
            side = serve_to

        dir_x = -1.0 if side == 'left' else 1.0
        angle = self.rng.uniform(-0.25, 0.25)
        self.ball_vx = dir_x * self.ball_speed
        self.ball_vy = angle * self.ball_speed

        return self.get_observation()

    def get_observation(self):
        return np.array([
            self.ball_x,
            self.ball_y,
            self.ball_vx,
            self.ball_vy,
            self.left_paddle_y,
            self.right_paddle_y
        ], dtype=np.float32)

    def step(self, actions):
        if self.done:
            return self.get_observation(), (0.0, 0.0), True, {'reason': 'already_done'}

        a_left, a_right = actions

        self.left_paddle_y = self._move_paddle(self.left_paddle_y, a_left)
        self.right_paddle_y = self._move_paddle(self.right_paddle_y, a_right)

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_y <= 0.0:
            self.ball_y = 0.0
            self.ball_vy = abs(self.ball_vy)
        elif self.ball_y >= self.board_size_y:
            self.ball_y = self.board_size_y
            self.ball_vy = -abs(self.ball_vy)

        reward_left = 0.0
        reward_right = 0.0
        info = {}

        if self.ball_x <= 0.0:
            if abs(self.ball_y - self.left_paddle_y) <= self.paddle_half:
                self._reflect_from_paddle('left')
            else:
                self.right_score += 1
                reward_right += 1.0
                reward_left -= 1
                info['score_event'] = 'right'
                self._serve_after_score(to='left')

        elif self.ball_x >= self.board_size_x:
            if abs(self.ball_y - self.right_paddle_y) <= self.paddle_half:
                self._reflect_from_paddle('right')
            else:
                self.left_score += 1
                reward_left += 1.0
                reward_right -= 1.0
                info['score_event'] = 'left'
                self._serve_after_score(to='right')

        self.steps += 1

        if (self.left_score >= self.max_score) or (self.right_score >= self.max_score) or (
                self.steps >= self.max_steps):
            self.done = True
            info['final_scores'] = (self.left_score, self.right_score)

        obs = self.get_observation()
        rewards = (float(reward_left), float(reward_right))
        return obs, rewards, bool(self.done), info

    def _move_paddle(self, y, action):
        y += action * self.paddle_speed

        if y + self.paddle_half >= self.board_size_y:
            y = self.board_size_y - self.paddle_half
        elif y <= 0:
            y = self.paddle_half

        return y

    def _reflect_from_paddle(self, side):
        if side == 'left':
            paddle_y = self.left_paddle_y
            self.ball_x = 0.0 + 1e-6
            self.ball_vx = abs(self.ball_vx) if self.ball_vx != 0 else self.ball_speed
        else:
            paddle_y = self.right_paddle_y
            self.ball_x = self.board_size_x - 1e-6
            self.ball_vx = -abs(self.ball_vx) if self.ball_vx != 0 else -self.ball_speed

        offset = (self.ball_y - paddle_y) / self.paddle_half
        offset = float(np.clip(offset, -1.0, 1.0))

        self.ball_vy = offset * (self.ball_speed + self.ball_speed_variation * self.rng.randn())

        min_speed = self.ball_speed * 0.7
        max_speed = self.ball_speed * 1.5
        target_speed = min_speed + (max_speed - min_speed) * abs(offset)

        speed = np.sqrt(self.ball_vx ** 2 + self.ball_vy ** 2)
        if speed == 0:
            speed = 1e-6
        scale = target_speed / speed
        self.ball_vx *= scale
        self.ball_vy *= scale

    def _serve_after_score(self, to='left'):
        print(self.ball_x, self.ball_y)
        self.ball_x = self.board_size_x / 2
        self.ball_y = self.board_size_y / 2
        dir_x = -1.0 if to == 'left' else 1.0
        angle = self.rng.uniform(-0.25, 0.25)
        self.ball_vx = dir_x * self.ball_speed
        self.ball_vy = angle * self.ball_speed
        time.sleep(1)

    def render(self, scale=40, caption="Pong", fps=60, margin_ratio=0.05):
        """
        Render the game using pygame with horizontal and vertical margins.
        - scale: pixels per board unit
        - margin_ratio: fraction of window used as horizontal/vertical margin
        """

        # --- Initialize pygame ---
        if not getattr(self, "_pygame_inited", False):
            pygame.init()
            self._W = int(self.board_size_x * scale)
            self._H = int(self.board_size_y * scale)
            self._screen = pygame.display.set_mode((self._W, self._H))
            pygame.display.set_caption(caption)
            self._clock = pygame.time.Clock()

            # Colors
            self._bg = (12, 12, 12)
            self._fg = (230, 230, 230)
            self._dim = (100, 100, 100)

            # Font
            try:
                self._font = pygame.font.SysFont("dejavusans", max(18, int(1.5 * scale)))
            except:
                self._font = pygame.font.Font(None, max(18, int(1.2 * scale)))

            self._pygame_inited = True
            self._pygame_running = True

        if not self._pygame_running:
            return

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self._pygame_running = False
                pygame.quit()
                return

        # --- Margins ---
        margin_x = int(margin_ratio * self._W)
        margin_y = int(margin_ratio * self._H)

        # --- Mapping functions ---
        def to_px_x(x):
            return margin_x + int(x / self.board_size_x * (self._W - 2 * margin_x))

        def to_px_y(y):
            return margin_y + int(y / self.board_size_y * (self._H - 2 * margin_y))

        # --- Clear screen ---
        self._screen.fill(self._bg)

        # --- Draw midline ---
        pygame.draw.line(self._screen, self._dim, (self._W // 2, margin_y), (self._W // 2, self._H - margin_y), 2)

        # --- Paddle sizes ---
        paddle_half_px = max(2, int(self.paddle_half / self.board_size_y * (self._H - 2 * margin_y)))
        paddle_w = max(4, int(0.01 * self._W))

        # --- Left paddle ---
        left_x = margin_x
        left_y = to_px_y(self.left_paddle_y)
        left_rect = pygame.Rect(left_x - paddle_w // 2, left_y - paddle_half_px, paddle_w, 2 * paddle_half_px)
        pygame.draw.rect(self._screen, self._fg, left_rect)

        # --- Right paddle ---
        right_x = self._W - margin_x
        right_y = to_px_y(self.right_paddle_y)
        right_rect = pygame.Rect(right_x - paddle_w // 2, right_y - paddle_half_px, paddle_w, 2 * paddle_half_px)
        pygame.draw.rect(self._screen, self._fg, right_rect)

        # --- Ball ---
        ball_r = max(2, int(0.02 * self._H))
        pygame.draw.circle(self._screen, self._fg, (to_px_x(self.ball_x), to_px_y(self.ball_y)), ball_r)

        # --- Scores ---
        score_surf = self._font.render(f"{self.left_score} - {self.right_score}", True, self._fg)
        score_rect = score_surf.get_rect(center=(self._W // 2, margin_y // 2))
        self._screen.blit(score_surf, score_rect)

        # --- Steps ---
        small_font = pygame.font.Font(None, max(12, int(0.03 * self._H)))
        steps_surf = small_font.render(f"steps: {self.steps}", True, (150, 150, 150))
        self._screen.blit(steps_surf, (5, self._H - margin_y))

        # --- Update screen ---
        pygame.display.flip()

        # --- FPS cap ---
        if fps and fps > 0:
            self._clock.tick(fps)


