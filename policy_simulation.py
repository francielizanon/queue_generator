from job import Job
from metrics import Metrics

#this is similar to play_execution from queue.py in the sense that we 
#try to play what will happen during the execution to collect metrics.
#However, here we take into consideration the number of I/O  nodes 
#given to each job and try to estimate I/O bandwidth.
#we will play the execution of a exp_queue of jobs on a cluster of node_nb
#processing nodes and ion_nb I/O nodes
#returns a Metrics object with all the calculated metrics
def simulate_execution_with_policy(exp_queue, node_nb, ion_nb, policy):
	clock = 0
	#makes a hard copy of exp_queue (below), otherwise python would
	#copy the reference to the list, and it would be modified in
	#this function (which we do not want to happen)
	queue = [job for job in exp_queue]  
	available_nodes = node_nb
	running = [] #it will keep the jobs while they are running
	jobid = 0
	metrics = Metrics()
	while(len(queue) > 0) or (len(running) > 0): #while there are 
					#applications either waiting or
					#still running
		#first we try to schedule jobs
		while (len(queue) > 0) and (queue[0].nodes <= available_nodes):
			running.append(Job(jobid,clock,queue[0]))
			jobid+=1
			available_nodes -= queue[0].nodes
			del queue[0]
		#now we know the set of jobs that will run concurrently
		#until the next event, so we have to decide the number 
		#of I/O nodes to each of them
		decisions = apply_policy(running, node_nb, ion_nb, policy, metrics, clock) 
		for job in running:
			job.update_io_nodes(decisions[job], clock)
		#now they will run until the first one ends its 
		#execution, so we go to that moment
		done,clock = get_next_finishing_jobs(running)
		for job in done:
			running.remove(job)
			available_nodes += job.app.nodes
		#end of the while, in the next iteration we will 
		#schedule more jobs before re-doing the decisions about
		#the I/O forwarding layer. If we cannot schedule more 
		#jobs, we will still do the new decisions because the 
		#set of running application has still changed (because 
		#some of them just finished)
	metrics.makespan = clock
	return metrics

#gets a list of jobs, estimate all their ending times, returns a list
#of the next ones to end (we could have multiple jobs ending at the 
#same time) AND the time that is going to happen.
def get_next_finishing_jobs(job_list):
	next_end = -1
	next_jobs= []
	for job in job_list:
		end_time = job.estimate_end_time()
		if (next_end == -1) or (next_end > end_time):
			next_end = end_time
			next_jobs = [job]
		elif next_end == end_time:
			next_jobs.append(job)
	return (next_jobs,next_end)
		
		
			 	
	
