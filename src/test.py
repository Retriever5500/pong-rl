from pong.single_agent import PongEnv
from stable_baselines3 import PPO

env = PongEnv(render_mode="human")
model = PPO.load("ppo_pong", env=env)

obs, info = env.reset()
for _ in range(10000):
    action, _states = model.predict(obs)
    obs, rewards, dones, trun, info = env.step(action)
    
env.close()
