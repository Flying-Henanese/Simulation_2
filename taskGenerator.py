import simpy
import random

Types = ['Streaming', 'imageProcessing', 'Computation']

def TaskGenerator(env, num, pipe):
	
	"""Tasks generated from things"""

	for i in range(1, num):
		yield env.timeout(random.randint(5,10))
		name = 'Task %d'%(i)
		dataSize = random.randint(1,100)
		computationCost = random.randint(1,100)
		TaskType = random.choice(Types)
		TimeStamp = env.now 

		Task = {'Name':name, 'ComputationCost':computationCost, 'DataSize':dataSize, 'TaskType':TaskType, 'TimeStamp':TimeStamp}

		yield pipe.put(task)