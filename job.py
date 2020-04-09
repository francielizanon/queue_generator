class Job:
	"""
	a job that will execute an application on the cluster
	during the experiment

	...

	Attributes
	----------
	jobid : int
		an identifier for this job 
	start_time : float
		the clock of the simulation when this application was
		scheduled to be executed (which is when this object 
		will be created)
	app : Application
		the Application object with information about what this
		job is running (including number of nodes, execution 
		time with different numbers of I/O nodes, etc)
	ion : int
		number of I/O nodes given to this application at the 
		moment (it will be updated during the simulation as 
		policies make new decisions)
	done : float
		between 0 and 1, tells how much of this execution has 
		already been done. Not always up-to-date, has to be 
		updated with a explicit call to the update_progress 
		method.
	previous_event : float
		the clock of when the previous change in the number of 
		I/O nodes was made. Used to estimate the progress.

	Methods
	-------
	update_io_nodes(ion, clock)
		changes the number of I/O nodes given to this 
		application (to ion). Before doing that, it calls
		update_progress to
		account for the time spent with the previous 
		configuration (so it requires the clock of this event)
	estimate_end_time():
		Giving the pace defined by the current number of I/O 
		nodes (see update_progress for an explanation), return
		the clock of the moment when this job is 
		expected to finish its execution.
	"""
	def __init__(self, jobid, start_time, app, ion=-1):
		self.jobid = jobid
		self.start_time = start_time
		self.previous_event = start_time
		self.app = app
		self.ion = ion
		self.done = 0.0

	def update_progress(self, clock):
		"""
		Calculates how much of this execution has been done
		since the last time we checked. Here we assume that
		execution advances in a constant pace given by the 
		expected runtime with the current number of I/O nodes.
		For instance, if an application takes 4s with 1 I/O 
		node, and was executed with this configuration for 2s,
		we say it was able to run 0.5 of its execution. If at 
		this point we change its number of I/O nodes to 4 and
		its runtime goes to 10s, each 1 second in the new 
		configuration will make it advance in 0.1 (1/10).
		
		Parameters
		----------
		clock : float
			the current clock
		"""
		if clock > self.previous_event:
			runtime = self.app.runtime[self.ion]
			self.done += (float(clock)-self.previous_event)/runtime
			assert self.done < 1.0 #it should not be 
				#possible for jobs to have ended when
				#we call this because we do this 
				#verification and advance the clock 
				#after applying the policy (and hence 
				#before the next loop iteration when we
				#are going to call this again)
		
	def update_io_nodes(self, ion, clock):
		"""
		changes the number of I/O nodes given to this 
		application (to ion). Before doing that, it calls
		update_progress to
		account for the time spent with the previous 
		configuration (so it requires the clock of this event)
		"""
		assert ion in self.app.runtime #make sure we have an
					#execution time of this app
					#with this number of I/O  nodes
		self.update_progress(clock)
		self.ion = ion
		self.previous_event = clock

	def estimate_end_time(self):
		"""
		Giving the pace defined by the current number of I/O 
		nodes (see update_progress for an explanation), return
		the clock of the moment when this job is 
		expected to finish its execution
		"""
		runtime = self.app.runtime[self.ion]
		return self.previous_event + ((1.0 - self.done)*runtime)
