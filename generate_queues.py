from random import seed,random
from application import Application
from queue import Queue
from output_file import OutputFile

####### PARAMETERS #####
input_file = "results-runtime.csv"  #with the path so we can find it
output_file = "random_queues.csv"   
debug = True 
node_nb = 96  #how many processing nodes
ion_nb = 12    #how many I/O nodes
minimum_time = 3600  #minimum experiment execution time in seconds
summary_method = "median"  #how should we combine multiple executions 
			#of the same applications with the same 
			#configuration to obtain an estimate for its 
			#execution time ("mean" or "median")
queue_nb = 1 #number of random queues to be generated and evaluated
########################

#reads information from the file and returns a list of Application
#objects containing the information
def read_runtime(filename):
	arq = open(filename, "r")
	contents = arq.readlines()
	arq.close()
	existing = {} #used to make sure each application is created
		#only once. relates (app, nodes, procs) to the 
		#corresponding Application object
	for line in contents:
		if "forwarders" in line:
			continue #skip the header
		#obtain information from the line
		parsed= line.split('\n')[0].split(';')
		assert len(parsed) == 7
		app = parsed[3]
		nodes = int(parsed[1])
		procs = int(parsed[2])
		size = (nodes, procs)
		ion = int(parsed[0])
		time = float(parsed[5])
		#store it
		if not (app, nodes, procs) in existing:
			new_app = Application(app, nodes, procs, debug)
			existing[(app, nodes, procs)] = new_app
		existing[(app, nodes, procs)].update_runtime(ion, time)
	#call the estimate_runtime method of all Application objects to
	#calculate the median execution time from all the observations
	#registered with the update_runtime method just above
	for app in existing:
		existing[app].estimate_runtime(summary_method)
	return list(existing.values())

#######################################################################
#first obtain information about the applications
apps = read_runtime(input_file)
print("Available applications: ")
print([str(app) for app in apps])
#now generate random queues and write them to the output file
#(for an explanation of the columns of the output file, see the 
#documentation of the Queue class)
header="queue;njobs;policy_calls;min_makespan;max_makespan;"
header+="median_njobs;mean_njobs;median_period;mean_period;"
header+="median_input_njobs;mean_input_njobs"
csv = OutputFile(output_file, header)
seed()
random_queues = []
while len(random_queues) < queue_nb:
	new_queue = Queue(apps, node_nb, ion_nb, minimum_time, debug)
	#here we can add filters to discard queues that are not what
	#we want
	if new_queue.median_input_njobs < 2:
		continue
	q = new_queue.encode()  #to understand how a queue of jobs is
			#represented by a single string, see the
			#application_encode.py file
	if not (q in random_queues):
		random_queues.append(q)
		csv.write(new_queue.get_output_line(q))
csv.close()

	
