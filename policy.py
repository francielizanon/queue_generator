def apply_policy(job_list, node_nb, ion_nb, policy, metrics, clock):
	if policy == "baseline":
		decision = baseline_policy(job_list, node_nb, ion_nb, metrics, clock)
	else:
		assert False
	metrics.register_policy_call(len(job_list), clock, decision)
	return decision
	
#the baseline policy has a fixed number of computing nodes assigned to 
#an I/O node
def baseline_policy(job_list, node_nb, ion_nb, metrics, clock):
	decisions={}
	for job in job_list:
		#we assume the number of I/O nodes is a divisor of the
		#number of computing nodes. That is checked in generate_queues.py
		assert (ion_nb*job.app.nodes)%node_nb == 0
		decisions[job] = (ion_nb*job.app.nodes)//node_nb 
	return decisions
