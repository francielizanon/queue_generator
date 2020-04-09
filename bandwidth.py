class Bandwidth():
	"""
	Used to access the bandwidth estimations for applications
	with different numbers of I/O nodes
	"""
	def __init__(self):
		#TODO read bandwidth from some file to some data structure
		self.bandwidth = {}
	
	def get(self, app, nodes, procs, ion):
		"""	
		given the name of the application app (as in the 
		results-runtime.csv file, the number of nodes, the
		number of processes procs, and the number of I/O nodes
		ion, retuns the bandwidth
		"""
		#TODO recover from the data strucure read in __init__
		#this will replace database_lookup from the original mckp code (no conversions required here, they are done there), and will also be used to collect metrics during the simulation
		return 1.0
