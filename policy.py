
	
def baseline_policy(job_list, node_nb, ion_nb):
	decisions={}
	for job in job_list:
		decisions[job] = (float(ion_nb)*job.app.nodes)//node_nb
	#TODO there is a huge problem to solve: 96/8 is not an integer division...
