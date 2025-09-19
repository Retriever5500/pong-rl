import gymnasium as gym
import numpy as np
import pygame

from .pong import Pong
from .pong_ai import simple_agent, better_agent


class PongEnv(gym.Env):
    def __init__(self, render_mode=None, ai_script="simple", board_size_x=20, board_size_y=10, max_score=5,
                 ball_speed=0.7, paddle_speed=0.4, paddle_half=1,
                 max_steps=100000):
        self.render_mode = render_mode
        self.ai_script = ai_script

        low = np.array([0, 0, -ball_speed * 1.5, -ball_speed * 1.5, 0, 0])
        high = np.array([board_size_x, board_size_y, ball_speed * 1.5, ball_speed * 1.5, board_size_y, board_size_y])
        self.observation_space = gym.spaces.Box(low, high, (6,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(3)

        self.pong = Pong(board_size_x=20, board_size_y=10, max_score=5, ball_speed=0.7, paddle_speed=0.4, paddle_half=1,
                         max_steps=100000)

    def reset(self, seed=0):
        return self.pong.reset()

    def step(self, action):
        # Action space is 0, 1 and 2 however the game takes -1, 0, and 1 as input so we substarct by one
        a_left = action - 1

        if self.ai_script == "simple":
            a_right = simple_agent(self.pong, "right")
        else:
            a_right = better_agent(self.pong, "right")

        obs, rewards, done, info = self.pong.step((a_left, a_right))
        reward = rewards[0]
        truncated = False

        if self.render_mode == "human":
            self.render()

        if 'score_event' in info:
            if info['score_event'] == 'right':
                self.pong.serve_after_score(to='left')
            else:
                self.pong.serve_after_score(to='right')

        return obs, reward, done, truncated, info

    def render(self):
        self.pong.render()

    def close(self):
        self.pong.close()
