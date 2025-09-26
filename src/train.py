from pong.single_agent import PongEnv
from stable_baselines3 import PPO

env = PongEnv(render_mode=None)

model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100000)
model.save("ppo_pong")
