import simpy
import random
import matplotlib.pyplot as plt
import numpy

Types = ['Streaming', 'ImageProcessing', 'Computation']#task types

env = simpy.Environment()#running environmrnt
#repeat simulation for times at different ratio
envs = []
#an array to store all experiment results
res = []
horizontal = []

Threshold = 10000
App_num = 20
#lifeTime_fog = 0
#lifeTime_cloud = 0

makespan = [0]*App_num
#utilization_cloud = [None]*2  

def TaskGenerator(env, num, pipe, app_num, start):

    """Tasks generated from things"""

    for i in range(1,num):
        yield env.timeout(numpy.random.poisson(20000,size=1))
        yield env.timeout(200)#gap between two succesive tasks
        name = 'Task %d'%(i)
        #dataSize = SizeSet[i-1]
        #dataSize = data[app_num-1]
        dataSize = DSizes[start+i-1]
        #computationCost = numpy.random.exponential(scale=20000, size=1)
        #computationCost = comp[app_num-1]
        computationCost = CompSizes[start+i-1]
        TaskType = random.choice(Types)
        TimeStamp = env.now 
        appNum = app_num
        ResUsage = random.randint(1,101)

        if i==num-1:
            flag=True 
        else:
            flag=False

        task = {'Name':name, 'ComputationCost':computationCost, 'DataSize':dataSize, 'TaskType':TaskType, 'TimeStamp':TimeStamp, 'APPNUM':appNum, 'ResUsage':ResUsage, 'LastOne':flag}

        yield pipe.put(task)

def data_transfer(env, pipe, pipe_fog, pipe_cloud, threshold):

    while True:
        BandWidth = 3
        task = yield pipe.get()
        computationCost = task['ComputationCost']
        dataSize = task['DataSize']

        if computationCost>threshold:#offload to cloud
            task['TimeStamp'] = task['TimeStamp'] - dataSize*50
            yield env.timeout(dataSize/BandWidth)
            yield pipe_cloud.put(task)
        else:
            task['TimeStamp'] = task['TimeStamp'] - dataSize*4
            yield env.timeout(dataSize/BandWidth)
            #print env.now
            yield pipe_fog.put(task)

        #yield env.timeout(dataSize/BandWidth)

def cloud(env, pipe_cloud):

    global lifeTime_cloud
    global makespan

    while True:
        task = yield pipe_cloud.get()
        compTime = task['ComputationCost']*1
        yield env.timeout(compTime)
        lifeTime_cloud = lifeTime_cloud + (env.now - task['TimeStamp'])
        name = task['Name']
        #if name=='Name %d'%(num-1):
        #    makespan = env.now
        if task['LastOne']==True:
            seq = task['APPNUM']-1 
            makespan[seq]=env.now 
            print 'task %d finished at %d'%(task['APPNUM'], env.now)

def fog(env, pipe_fog):

    global lifeTime_fog
    global makespan

    while True:
        task = yield pipe_fog.get()
        compTime = task['ComputationCost']*10
        gap = env.now - task['TimeStamp']
        yield env.timeout(compTime)
        lifeTime_fog = lifeTime_fog+(env.now - task['TimeStamp'])
        #if task['Name']=='Name %d'%(num-1):
        #    makespan = env.now
        if task['LastOne']==True:
            makespan[task['APPNUM']-1]=env.now 
            print 'task %d finished at %d'%(task['APPNUM'], env.now)   

for i in range(1,101):
    envs.append(simpy.Environment())

#index = 0
taskNum = [0]*App_num
CompSizes = []
DSizes = []
for i in range(App_num):#10 apps run in paralell
    taskNum[i] = random.randint(75,125)

for i in range(App_num):
    for x in numpy.random.exponential(scale=20000, size=taskNum[i-1]):
        CompSizes.append(x)
        DSizes.append(x*random.randint(20,30)/10)

#set the start point of each group of numbers
points = [] 
points.append(0)
for i in range(1,App_num):
    points.append(sum(taskNum[0:i]))

for e in envs:
    #makespan = 0
    lifeTime_fog = 0
    lifeTime_cloud =0
    pipe = simpy.Store(e)
    #pipe_fog = [simpy.Store(e)]*5
    pipe_fog = simpy.Store(e)
    pipe_cloud = simpy.Store(e)

    for i in range(App_num):#generate 10 apps
        e.process(TaskGenerator(e, taskNum[i], pipe, i, points[i]))
    #e.process(TaskGenerator(e, taskAmount, pipe,0))
    e.process(data_transfer(e, pipe, pipe_fog, pipe_cloud,Threshold))
    f_0 = e.process(fog(e, pipe_fog))
    f_1 = e.process(fog(e, pipe_fog))
    f_2 = e.process(fog(e, pipe_fog))
    f_3 = e.process(fog(e, pipe_fog))
    f_4 = e.process(fog(e, pipe_fog))
    c_0 = e.process(cloud(e, pipe_cloud))
    c_1 = e.process(cloud(e,pipe_cloud))
    e.run(until=None)
    print 'Total makespan is %.2f for processing this applicatino of %d tasks'%((lifeTime_cloud+lifeTime_fog)/10000, 10000)
    
    print 'Threshold is %d'%(Threshold)
    res.append((lifeTime_fog+lifeTime_cloud)/10)
    horizontal.append(Threshold)
    Threshold = Threshold + 200
    #taskAmount = taskAmount + 500
    #index = index +1

plt.plot(horizontal,res)
plt.show()