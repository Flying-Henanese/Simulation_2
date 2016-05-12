import simpy
import random
import matplotlib.pyplot as plt 

Types = ['Streaming', 'ImageProcessing', 'Computation']#task types

env = simpy.Environment()#running environmrnt

#repeat simulation for times at different ratio
envs = []

#an array to store all experiment results
res = []
horizontal = []

Threshold = 500
taskAmount= 30000
#lifeTime_fog = 0
#lifeTime_cloud = 0

def TaskGenerator(env, num, pipe):

	"""Tasks generated from things"""

	for i in range(1,num):
		yield env.timeout(1)#gap between two succesive tasks
		name = 'Task %d'%(i)
		dataSize = random.randint(800,2000)
		computationCost = random.randint(500,800)
		TaskType = random.choice(Types)
		TimeStamp = env.now 

		task = {'Name':name, 'ComputationCost':computationCost, 'DataSize':dataSize, 'TaskType':TaskType, 'TimeStamp':TimeStamp}

		yield pipe.put(task)

def data_transfer(env, pipe, pipe_fog, pipe_cloud, threshold):

	while True:
		BandWidth = 3
		task = yield pipe.get()
		computationCost = task['ComputationCost']
		dataSize = task['DataSize']

		if computationCost>threshold:
			task['TimeStamp'] = task['TimeStamp']-dataSize*10
			yield env.timeout(dataSize/BandWidth)
			yield pipe_cloud.put(task)
		else:
			task['TimeStamp'] = task['TimeStamp'] - dataSize
			yield env.timeout(dataSize/BandWidth)
			#print env.now
			yield pipe_fog.put(task)

		#yield env.timeout(dataSize/BandWidth)

def cloud(env, pipe_cloud):

	global lifeTime_cloud

	while True:
		task = yield pipe_cloud.get()
		compTime = task['ComputationCost']*1
		yield env.timeout(compTime)
		lifeTime_cloud = lifeTime_cloud + (env.now - task['TimeStamp'])

def fog(env, pipe_fog):

	global lifeTime_fog

	while True:
		task = yield pipe_fog.get()
		compTime = task['ComputationCost']*5
		gap = env.now - task['TimeStamp']
		yield env.timeout(compTime)
		lifeTime_fog = lifeTime_fog+(env.now - task['TimeStamp'])

for i in range(1,22):
	envs.append(simpy.Environment())

#index = 0

for e in envs:
    lifeTime_fog = 0 
    lifeTime_cloud =0
    pipe = simpy.Store(e)
    pipe_fog = simpy.Store(e)
    pipe_cloud = simpy.Store(e)
    e.process(TaskGenerator(e, taskAmount, pipe))
    e.process(data_transfer(e, pipe, pipe_fog, pipe_cloud,Threshold))
    e.process(fog(e, pipe_fog))
    e.process(cloud(e, pipe_cloud))
    e.run(until=100000000)
    print 'Total time spent is %.2f for processing %d tasks'%((lifeTime_fog+lifeTime_cloud)/10000000 , taskAmount)
    print 'Threshold is %d'%(Threshold)
    res.append(lifeTime_fog+lifeTime_cloud)
    horizontal.append(Threshold)
    #taskAmount = taskAmount + 500
    #index = index +1
    Threshold = Threshold + 15

plt.plot(horizontal,res)
plt.show()
