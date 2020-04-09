from heapq import heappop,heappush
from random import randint
from numpy import median,mean
from application import Application
from application_encode import encode_application
from policy_simulation import simulate_execution_with_policy
from metrics import Metrics

class Queue:
	"""
	A list of jobs to be executed in order

	...

	Attributes
	----------
	jobs : List[Application]
		the queue as an ordered list of Application objects
	min_makespan : float
		a lower bound for the execution time of this queue. It 
		cannot be shorter than this (but this lower bound 
		itself may be impossible to attain)
	max_makespan : float
		an upper bound for the execution time of this queue. It
		cannot be longer than this (but this upper bound itself
		may be impossible to attain)
	baseline_metrics : Metrics
		metrics obtained from simulating the generated queue 
		with the baseline policy (where the connection between 
		computing and I/O nodes is fixed
	mckp_metrics : Metrics
		metrics obtained from simulating the generated queue
		with the mckp policy
	"""
	def __init__(self, apps, node_nb, ion_nb, min_time, debug, bandwidth_getter):
		"""
		Generates a random queue respecting given constraints.
		Then calculates some metrics on this queue that will
		eventually allow us to select the best queues.
		Additional rules : 
		1. all applications must be executed at least once 
		   during the experiment

		Parameters
		----------
		apps : List[Application]
			a list of Application objects
		node_nb : int
			the number of processing nodes 
		min_time : float
			the minimum duration for the experiment in 
			seconds
		"""
		done = False
		while not done:
			if debug:
				print("will generate a queue...")
			self.jobs = make_a_queue(apps, node_nb, min_time, debug)
			if debug:
				print("generated a queue of "+str(len(self.jobs))+" jobs")
			done = are_all_applications_executed(self.jobs, apps)
			if (not done) and debug:
				print("Made a queue of "+str(len(self.jobs))+" jobs, but not all applications are present, so we'll try again.")
		self.min_makespan = calculate_makespan(self.jobs, node_nb, "best")
		self.max_makespan = calculate_makespan(self.jobs, node_nb, "worst")
		if debug:
			print("Will simulate it with the baseline policy")
		self.baseline_metrics = simulate_execution_with_policy(self.jobs, node_nb, ion_nb, "baseline", bandwidth_getter)
		if debug:
			print("Will simulate it with the mckp policy")
		self.mckp_metrics = simulate_execution_with_policy(self.jobs, node_nb, ion_nb, "mckp", bandwidth_getter)
	
	def encode(self):
		"""
		returns a string representation of this queue as a 
		series of letters, where each letter represents an 
		application.
		"""
		encoded_list = [encode_application(app) for app in self.jobs]
		ret = ""
		for elem in encoded_list:
			ret+= elem
		return ret

	def get_output_line(self, encoded):
		"""
		Returns the string ready to be written to the output 
		file, containing information about this queue.
		
		Parameters
		----------
		encoded : str
			the output obtained from calling the method 
			encode of this object
		"""
		assert encoded != ""
		ret = encoded + ";"+str(len(self.jobs))+";"
		ret += str(self.min_makespan)+";"
		ret += str(self.max_makespan)+";"
		ret += str(self.baseline_metrics.makespan)+";"
		ret += str(self.mckp_metrics.makespan)+";"
		ret += str(self.baseline_metrics.mean_bandwidth)+";"
		ret += str(self.mckp_metrics.mean_bandwidth)+";"
		ret += str(self.baseline_metrics.median_bandwidth)+";"
		ret += str(self.mckp_metrics.median_bandwidth)+";"
		ret += str(self.baseline_metrics.max_bandwidth)+";"
		ret += str(self.mckp_metrics.max_bandwidth)+";"
		ret += str(self.mckp_metrics.policy_calls)+";"
		ret += str(self.mckp_metrics.changes)+";"
		ret += str(self.mckp_metrics.median_period)+";"
		ret += str(self.mckp_metrics.mean_period)+";"
		ret += str(self.mckp_metrics.median_njobs)+";"
		ret += str(self.mckp_metrics.mean_njobs)+";"
#		ret += str()+";"
		return ret+"\n"	

#given a queue of jobs to be executed, answer if all applications in 
#the apps list are present among these jobs.
def are_all_applications_executed(queue, apps):
	present = {}
	for app in queue:
		present[app] = True
	if len(list(present.keys())) != len(apps):
		return False
	else:
		return True

#generates and returns a random queue of jobs running applications 
#among the ones listed in apps on a cluster or node_nb processing 
#nodes. The generated queue must respect a constraints : the
#optimistic execution time must be longer or equal to min_time
def make_a_queue(apps, node_nb, min_time, debug=False):
	queue = []
	#Note: it would be best here to calculate the makespan
	#incrementally as we add stuff to the queue, instead of 
	#replaying the whole queue each time. This was lazy programming
	#and should be changed if the execution time of this script 
	#becomes a problem
	while calculate_makespan(queue, node_nb, "best") < min_time:
		app = randint(0,len(apps)-1)
		queue.append(apps[app])
		if debug:
			print("adding a job for application "+str(apps[app])+", now our optimistic execution time is "+str(calculate_makespan(queue, node_nb, "best")))
	return queue
	
#play the execution of the queue with FIFO scheduler on a cluster
#of node_nb processing nodes to see how long it
#would take in an optimistic (which_time = "best") or pessimistic 
#(which_time = "worst"). This estimation does NOT take into account the
#choices that will be made by the I/O forwarding policy or the number 
#of available I/O nodes, in fact the obtained makespan may be 
#impossible for this queue. It is used just to give lower and upper 
#bounds on the actually execution time of the experiment.
#Returns the makespan
def calculate_makespan(queue, node_nb, which_time,debug=False): 
	events=[] #a heap of events where we will put the end
		#of applications so we can schedule new ones
		#and advance in time towards the end of the
		#execution
	clock = 0
	#makes a hard copy of the queue (below), otherwise python would
	#copy the reference to the list, and it would be modified in
	#this function (which we do not want to happen)
	this_queue = [job for job in queue]  
	available_nodes = node_nb
	current_conc_nb = 0   #the number of concurrent jobs in execution
	if debug:
		print("Will start the \"simulation\" with "+str(node_nb)+" nodes and queue: "+str([str(app) for app in this_queue]))
	while (len(this_queue) > 0) or (len(events) > 0): 
		#if we have available resources and jobs to
		#schedule, do so. 
		while (len(this_queue) > 0) and (this_queue[0].nodes <= available_nodes):
			available_nodes -= this_queue[0].nodes
			end_time = clock + this_queue[0].get_time(which_time)
			heappush(events, (end_time, this_queue[0]))
			if debug:
				print("Scheduled "+str(this_queue[0]) +", available = "+str(available_nodes)) 
			del this_queue[0]
			current_conc_nb += 1
			
		#we cannot schedule more jobs, so fastforward 
		#to the moment where the next one finishes its
		#execution
		event = heappop(events)
		clock = event[0]
		available_nodes += event[1].nodes
		current_conc_nb -= 1
		if debug:
			print("clock = "+str(clock)+", end of "+str(event[1])+", available = "+str(available_nodes))
	return clock
				
				
