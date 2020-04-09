from numpy import median,mean
from bandwidth import Bandwidth

class Metrics:
	"""
	Used to keep track of metrics while simulating the execution of
	policies.
	These metrics assume register_policy_call is called EVERY TIME
	the policy is applied, and that the policy is applied every 
	time the set of running application changes for some time.

	Attributes
	----------
	policy_calls : int
		how many times the policy was applied
	last_clock : float
		the clock of the last time the policy was 
		applied,so we can calculate time between calls
	period : List[float]
		a list with all the times between consecutive calls to 
		the policy
	median_period and mean_period : float
		the median and the mean of the period list
	makespan : float
		the time it took to run the whole queue
	njobs : List[int]
		a list with the number of jobs given as input to each 
		call of the policy
	median_njobs and mean_njobs : float
		the median and the mean of the njobs list
	changes : int
		number of policy calls where decisions have changed for
		at least one of the applications that were executing in
		the last time the policy was applied 
	last_decision : dict {Job, int}
		we keep the previous decision so we can check what 
		changed 
	bandwidth : List[float]
		a list with the global bandwidth every second
	median_bandwidth, mean_bandwidth, max_bandwidth : float
		median, mean, and maximum bandwidth
	previous_bandwidth : float
		used so we can register the previously obtained 
		bandwidth for how long it happened (which we will only
		know the next time the policy is called)
	bandwidth_getter : Bandwidth
		a reference to the Bandwidth object used to obtain 
		bandwidth of different combinations of application
		and number of I/O nodes
	
	Methods
	-------
	register_policy_call(job_nb)
		called by the policy every time it is applied to update
		the metrics
	summarize_policy_metrics(clock)
		it MUST be called at the end of the simulation to 
		calculate the means and medians, and to set the
		makespan to clock
	"""
	def __init__(self, bandwidth_getter):
		self.bandwidth_getter = bandwidth_getter
		self.policy_calls = 0
		self.last_clock = -1.0
		self.period = []
		self.median_period = -1.0
		self.mean_period = -1.0
		self.makespan = -1
		self.njobs = []
		self.median_njobs = -1.0
		self.mean_njobs = -1.0
		self.changes = -1
		self.bandwidth = []
		self.median_bandwidth = -1.0
		self.mean_bandwidth = -1.0
		self.max_bandwidth = -1.0
		self.previous_bandwidth = -1.0

	def summarize_policy_metrics(self, clock):
		if (self.last_clock >= 0) and (clock > self.last_clock):
			#we have to register the last bandwidth we observed
			self.bandwidth.extend([self.previous_bandwidth for i in range(int(self.last_clock), int(clock))])
		self.makespan = clock
		self.median_period = median(self.period)
		self.mean_period = mean(self.period)
		self.median_bandwidth = median(self.bandwidth)
		self.mean_bandwidth = mean(self.bandwidth)
		self.max_bandwidth = max(self.bandwidth)
		self.median_njobs = median(self.njobs)
		self.mean_njobs = mean(self.njobs)
		
	def register_policy_call(self, job_nb, clock, decision, debug=False):
		"""
		Parameters
		----------
		job_nb : int
			the number of jobs
		clock : float
			current clock
		"""
		self.policy_calls += 1
		#calculate bandwidth
		global_band = 0.0
		for job in decision:
			global_band += self.bandwidth_getter.get(job.app.app, job.app.nodes, job.app.procs, decision[job])
		if debug:
			print("The new global bandwidth is "+str(global_band))
		#time between consecutive calls to the policy
		if self.last_clock >= 0:
			assert clock >= self.last_clock  
			self.period.append(clock-self.last_clock)
			if debug:
				print("Registering the previous bandwidth of "+str(self.previous_bandwidth)+" from times "+str(int(self.last_clock))+" to "+str(int(clock)))
			self.bandwidth.extend([self.previous_bandwidth for i in range(int(self.last_clock), int(clock))])
		self.last_clock = clock
		self.previous_bandwidth = global_band
		#number of jobs given as input
		self.njobs.append(job_nb)
		#number of calls where decisions changed for 
		#applications that were running
		#the last time we applied the policy
		if self.changes == -1:
			self.changes = 0
		else:
			changed = False
			for job in decision:
				if job in self.last_decision:
					if self.last_decision[job] != decision[job]:
						changed = True
						break
			if changed:
				self.changes += 1
		self.last_decision = decision
	
