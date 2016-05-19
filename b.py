import simpy
import random
import matplotlib.pyplot as plt 

Types = ['Streaming', 'ParaTask', 'Computation']#task types

env = simpy.Environment()#running environmrnt

#repeat simulation for times at different ratio
envs = []

#an array to store all experiment results
res = []
horizontal = []

"""
Tasks have been categorized in 3 types and have different specifictions 
"""

Threshold = 15000
taskAmount= 1000
#lifeTime_fog = 0
#lifeTime_cloud = 0

makespan = 0

def TaskGenerator(env, num, pipe):#finished, waited to be debugged

    """Tasks generated from things"""
    for i in range(1, num):
        yield env.timeout(5)
        TaskType = random.choice(Types)
        name = 'Task %d'%(i)

        if TaskType == 'Streaming':
            dataSize = random.randint(20000,50000)
            computationCost = random.randint(1000,4000)
        elif TaskType == 'ParaTask':
            dataSize = random.randint(8000,15000)
            computationCost = random.randint(100000,500000)
        else:
            dataSize = random.randint(1000,2000)
            computationCost = random.randint(5000,10000)

        TimeStamp = env.now 
        task = {'Name':name, 'ComputationCost': computationCost, 'DataSize':dataSize, 'TaskType':TaskType, 'TimeStamp':TimeStamp}

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

def cloud(env, pipe_cloud, num):

    global lifeTime_cloud
    global makespan

    while True:
        task = yield pipe_cloud.get()
        compTime = task['ComputationCost']*1
        yield env.timeout(compTime)
        lifeTime_cloud = lifeTime_cloud + (env.now - task['TimeStamp'])
        name = task['Name']
        if name=='Name %d'%(num-1):
            makespan = env.now

def fog(env, pipe_fog, num):

    global lifeTime_fog
    global makespan

    while True:
        task = yield pipe_fog.get()
        compTime = task['ComputationCost']*5
        gap = env.now - task['TimeStamp']
        yield env.timeout(compTime)
        lifeTime_fog = lifeTime_fog+(env.now - task['TimeStamp'])
        if task['Name']=='Name %d'%(num-1):
            makespan = env.now
            

for i in range(1,88):
    envs.append(simpy.Environment())

#index = 0

for e in envs:
    makespan = 0
    lifeTime_fog = 0
    lifeTime_cloud =0
    pipe = simpy.Store(e)
    pipe_fog = simpy.Store(e)
    pipe_cloud = simpy.Store(e)
    e.process(TaskGenerator(e, taskAmount, pipe))
    e.process(data_transfer(e, pipe, pipe_fog, pipe_cloud,Threshold))
    p1 = e.process(fog(e, pipe_fog,taskAmount))
    p2 = e.process(fog(e, pipe_fog,taskAmount))
    p3 = e.process(fog(e, pipe_fog,taskAmount))
    p4 = e.process(fog(e, pipe_fog,taskAmount))
    e.process(cloud(e, pipe_cloud,taskAmount))
    e.run(until=None)
    print 'Total makespan is %.2f for processing this applicatino of %d tasks'%((e.now)/10000, taskAmount)
    print 'Threshold is %d'%(Threshold)
    res.append(e.now)
    horizontal.append(Threshold)
    Threshold = Threshold + 150
    #taskAmount = taskAmount + 500
    #index = index +1

plt.plot(horizontal,res)
plt.show()