from heapq import heappop,heappush
from random import randint
from numpy import median,mean
from application import Application
from application_encode import encode_application

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
	median_njobs and mean_njobs : float
		the median and mean number of concurrent jobs during 
		the execution, taken from a list of one measurement per
		second (so considering the time)
	median_period and mean_period : float
		the median and mean time between consecutive calls to
		the policy (which will decide how many I/O nodes to use
		to each application)
	policy_calls : int
		number of calls to the policy
	median_input_njobs and mean_input_njobs : float
		median and mean number of concurrent jobs given as
		input to the policy (similar to {median, mean}_njobs, 
		except that metric considers the time, while this one 
		just takes the number of concurrent jobs at each policy 
		call)
	"""
	def __init__(self, apps, node_nb, min_time, debug):
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
		metrics = play_execution(self.jobs, node_nb, "best")
		self.min_makespan = metrics[0]
		self.median_njobs = metrics[1]
		self.mean_njobs = metrics[2]
		self.median_period = metrics[3]
		self.mean_period = metrics[4]
		self.median_input_njobs = metrics[5]
		self.mean_input_njobs = metrics[6]
		self.policy_calls = metrics[7]
		self.max_makespan = calculate_makespan(self.jobs, node_nb, "worst")
		#TODO evaluate with policies
	
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
		ret += str(self.policy_calls)+";"
		ret += str(self.min_makespan)+";"
		ret += str(self.max_makespan)+";"
		ret += str(self.median_njobs)+";"
		ret += str(self.mean_njobs)+";"
		ret += str(self.median_period)+";"
		ret += str(self.mean_period)+";"
		ret += str(self.median_input_njobs)+";"
		ret += str(self.mean_input_njobs)+";"
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
			print("adding a job for application "+str(apps[app])+", now our optimistic execution time is "+str(calculate_makespan(queue, node_nb, "best", debug)))
	return queue
	
#see play_execution
def calculate_makespan(queue, node_nb, which_time, debug=False):
	return play_execution(queue, node_nb, which_time, debug)[0]

#play the execution of the queue with FIFO scheduler on a cluster
#of node_nb processing nodes to see how long it
#would take in an optimistic (which_time = "best") or pessimistic 
#(which_time = "worst"). This estimation does NOT take into account the
#choices that will be made by the I/O forwarding policy or the number 
#of available I/O nodes, in fact the obtained makespan may be 
#impossible for this queue. It is used just to give lower and upper 
#bounds on the actually execution time of the experiment.
#
#Returns metrics on the execution: 
#(makespan, 
#median number of concurrent jobs, 
#mean number of concurrent jobs, 
#median time between possible changes, 
#mean time between possible changes, 
#median number of jobs that would be given as input to the policy calls
#mean number of jobs that would be given as input to the policy calls,
#total number of calls to the policy)
#
#"possible changes" here refers to when a policy will be applied to 
#decide the number of I/O nodes for all running applications
def play_execution(queue, node_nb, which_time,debug=False): 
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
	concurrent_nb = []   #to keep track of the number of concurrent 
			#jobs during the simulation
	time_between_events = [] #to keep track of time between possible
			# changes in the decisions
	input_jobnb = [] #to keeo track of the number of jobs that 
			#would be the input for the policy
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
		if int(event[0]) > int(clock):
			concurrent_nb.extend([current_conc_nb for i in range(int(clock), int(event[0]))])
		time_between_events.append(event[0] - clock)
		input_jobnb.append(current_conc_nb)
		clock = event[0]
		available_nodes += event[1].nodes
		current_conc_nb -= 1
		if debug:
			print("clock = "+str(clock)+", end of "+str(event[1])+", available = "+str(available_nodes))
	return (clock, median(concurrent_nb), mean(concurrent_nb), median(time_between_events), mean(time_between_events), median(input_jobnb), mean(input_jobnb), len(input_jobnb))
				
				
