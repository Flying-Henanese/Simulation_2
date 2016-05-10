import simpy
import random

def fog(env, pipe):
	while True:
		task = pipe.get()
		computationCost = task['ComputationCost']
		yield env.timeout(computationCost)
		lifeTime = env.now-task['TimeStamp']