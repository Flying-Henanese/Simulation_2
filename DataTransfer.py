import simpy

def data_transfer(env, pipe, pipe_fog, pipe_cloud):

	while True:

	    Bandwidth = 15

	    task = yield pipe.get()
	    compCost = task['ComputationCost']
	    dataSize = task['DataSize']
	    #to simulate real transfer delay

	    if compCost > 50:
	    	task['TimeStamp'] = task['TimeStamp'] - dataSize/50#propagation delay
		    yield pipe_cloud.put(task)
	    else:
	    	task['TimeStamp'] = task['TimeStamp'] - dataSize/10#propagation delay
		    yield pipe_fog.put(task)

	    yield env.timeout(dataSize/Bandwidth)#transfer delay