from job import Job
from metrics import Metrics
from policy import apply_policy

#this is similar to play_execution from queue.py in the sense that we 
#try to play what will happen during the execution to collect metrics.
#However, here we take into consideration the number of I/O  nodes 
#given to each job and try to estimate I/O bandwidth.
#we will play the execution of a exp_queue of jobs on a cluster of node_nb
#processing nodes and ion_nb I/O nodes
#returns a Metrics object with all the calculated metrics
def simulate_execution_with_policy(exp_queue, node_nb, ion_nb, policy, bandwidth_getter, debug=False):
	clock = 0
	#makes a hard copy of exp_queue (below), otherwise python would
	#copy the reference to the list, and it would be modified in
	#this function (which we do not want to happen)
	queue = [job for job in exp_queue]  
	available_nodes = node_nb
	running = [] #it will keep the jobs while they are running
	jobid = 0
	metrics = Metrics(bandwidth_getter)
	if debug:
		print("Will start the simulation with "+str(node_nb)+" computing nodes, "+str(ion_nb)+" I/O nodes, and queue: "+str([str(app) for app in queue]))
	while(len(queue) > 0) or (len(running) > 0): #while there are 
					#applications either waiting or
					#still running
		#first we try to schedule jobs
		while (len(queue) > 0) and (queue[0].nodes <= available_nodes):
			running.append(Job(jobid,clock,queue[0]))
			jobid+=1
			available_nodes -= queue[0].nodes
			if debug:
				print("Scheduled "+str(queue[0]) +", available = "+str(available_nodes)) 
			del queue[0]
		#now we know the set of jobs that will run concurrently
		#until the next event, so we have to decide the number 
		#of I/O nodes to each of them
		decisions = apply_policy(running, node_nb, ion_nb, policy, metrics, clock, debug) 
		for job in running:
			job.update_io_nodes(decisions[job], clock)
		if debug:
			print("Made new decisions about the number of I/O nodes:")
			for job in decisions:
				print(str(job.app)+"\t"+str(decisions[job]))
		#now they will run until the first one ends its 
		#execution, so we go to that moment
		done,new_clock = get_next_finishing_jobs(running, clock)
		if new_clock <= clock:
			print("WARNING! The simulation is going from "+str(clock)+" to "+str(new_clock))
		clock = new_clock
		for job in done:
			running.remove(job)
			available_nodes += job.app.nodes
			if debug:
				print("End of job "+str(job.app)+", available nodes = "+str(available_nodes))
		if debug:
			print("---------------------------------------------------")
		#end of the while, in the next iteration we will 
		#schedule more jobs before re-doing the decisions about
		#the I/O forwarding layer. If we cannot schedule more 
		#jobs, we will still do the new decisions because the 
		#set of running application has still changed (because 
		#some of them just finished)
	metrics.summarize_policy_metrics(clock)
	return metrics

#gets a list of jobs, estimate all their ending times, returns a list
#of the next ones to end (we could have multiple jobs ending at the 
#same time) AND the time that is going to happen.
def get_next_finishing_jobs(job_list, clock, debug=False):
	next_end = -1
	next_jobs= []
	if debug:
		print("We'll look for the next jobs to finish")
	for job in job_list:
		end_time = job.estimate_end_time()
		if debug:
			print("job "+str(job.app)+" will go until "+str(end_time))
		if (next_end == -1) or (next_end > end_time):
			next_end = end_time
			next_jobs = [job]
		elif next_end == end_time:
			next_jobs.append(job)
	if debug:
		print("returning "+str([str(job.app) for job in next_jobs]))
	return (next_jobs,next_end)
		
		
