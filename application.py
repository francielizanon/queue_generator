from numpy import median,mean

class Application:
	"""	
	An application to be executed during the experiment

	...

	Attributes
	----------
	app : str
		the name of the application 
	nodes : int
		number of nodes to be used
	procs : int
		number of processes to be executed
	runtime : dict {int, float}
		a dictionary containing, to each number of I/O nodes, 
		the expected runtime of this application
	observations : dict {int, List[float]}
		a dictionary containing, to each number of I/O nodes,
		the observed runtime of different executions of this
		application with that number of I/O nodes. The idea is
		that this dict is filled with the update_runtime
		function. Then, after all information on executions was
		parsed, the estimate_runtime function has to be called
		to fill the runtime dictionary with the median 
		execution times
	best_time : float
		the time that would be obtained with the best decision
	worst_time : float
		the time that would be obtained with the worst decision 
	debug : boolean
		if we should print debug messages or not
	Methods
	-------
	"""
	def __init__(self,app, nodes, procs, debug):
		self.app = app
		self.nodes = nodes
		self.procs = procs
		self.runtime = {}
		self.observations = {}
		self.debug = debug

	def update_runtime(self, ion, time):
		"""
		Registers a runtime of this application with
		a given number of I/O nodes.

		Parameters
		----------
		ion : int
			number of I/O nodes
		time : float
		"""	
		if self.debug:
			print("adding execution time of "+str(self)+" with "+str(ion)+" I/O nodes: " + str(time))
		if not (ion in self.observations):
			self.observations[ion] = []
		self.observations[ion].append(time)

	def estimate_runtime(self, method):
		"""
		Takes the median or the mean (depending on what is said
		by the parameter method) of the times observed for each
		number
		of I/O nodes and store these values in the runtime 
		dictionary. Also find best_time and worst_time.
		"""
		assert (method == "median") or (method == "mean")
		for ion in self.observations:
			if method == "median":
				self.runtime[ion] = median(self.observations[ion])
			else:
				self.runtime[ion] = mean(self.observations[ion])
			if self.debug:
				print(method+" runtime for "+str(self)+" with "+str(ion)+" I/O nodes: "+str(self.runtime[ion]))
		self.best_time = min(list(self.runtime.values()))
		self.worst_time = max(list(self.runtime.values()))
	
	def get_time(self, which):
		if which == "best":
			return self.best_time
		elif which == "worst":
			return self.worst_time
		else:
			assert False

	def __lt__(self, other):
		return self.app < other.app

	def __str__(self):
		return "("+self.app+", "+str(self.nodes)+" nodes, "+str(self.procs)+" procs)"
