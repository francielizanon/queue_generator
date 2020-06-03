import numpy
from bandwidth import Bandwidth 

def apply_policy(job_list, node_nb, ion_nb, policy, metrics, clock, debug=False):
    if policy == "baseline":
        decision = baseline_policy(job_list, node_nb, ion_nb)
    elif policy == "mckp":
        decision = mckp_policy(job_list, node_nb, ion_nb, metrics.bandwidth_getter)
    else:
        assert False
    metrics.register_policy_call(len(job_list), clock, decision, debug)
    return decision
    
#the baseline policy has a fixed number of computing nodes assigned to 
#an I/O node
def baseline_policy(job_list, node_nb, ion_nb):
    decisions={}
    for job in job_list:
        #we assume the number of I/O nodes is a divisor of the
        #number of computing nodes. That is checked in generate_queues.py
        assert (ion_nb*job.app.nodes)%node_nb == 0
        decisions[job] = (ion_nb*job.app.nodes)//node_nb 
        assert decisions[job] > 0
    return decisions

#copied and adapted the MCKP policy from the code written by Jean Bez
def mckp_policy(job_list, node_nb, ion_nb, bandwidth_getter):
    # TODO: make this more dynamic
    avaible_forwarders = [1, 2, 4, 8]
    values = {}
    weight = {}
    groups = {}
    for group_id,job in enumerate(job_list):
        values[group_id] = []
        weight[group_id] = []
        groups[group_id] = []
        for nodes in avaible_forwarders:
            # Since we need to use integers and we are 
            #using five precision points, convert it
            values[group_id].append(int(bandwidth_getter.get(job.app.app, job.app.nodes, job.app.procs, nodes)* 100000.0))
            weight[group_id].append(nodes)
    table = numpy.zeros((len(job_list), ion_nb + 1), dtype=int)
    solution_table = numpy.zeros((len(job_list), len(avaible_forwarders), ion_nb + 1),dtype=int)
    for i in range(0, len(avaible_forwarders)):
        if weight[0][i] <= ion_nb:
            table[0][weight[0][i]] = max(table[0][weight[0][i]], values[0][i])
            solution_table[0][i][0] = table[0][weight[0][i]]
    for j in range(0, len(avaible_forwarders)):
        for k in range(0, ion_nb + 1):
            if k > 0:
                solution_table[0][j][k] = solution_table[0][j][0]
    for i in range(1, len(job_list)):
        for j in range(0, len(avaible_forwarders)):
            for k in range(0, ion_nb + 1):
                if k < weight[i][j]:
                    solution_table[i][j][k] = solution_table[i][j - 1][k]
                elif table[i - 1][k - weight[i][j]] > 0:
                    table[i][k] = max(table[i][k], table[i - 1][k - weight[i][j]] + values[i][j])
                    solution_table[i][j][k] = table[i][k]
                else:
                    solution_table[i][j][k] = table[i][k]
    index_max = 0
    index_max_solution = 0
    for i in range(0, ion_nb + 1):
        if index_max_solution <= solution_table[len(weight) - 1][len(avaible_forwarders) - 1][i]:
            index_max_solution = solution_table[len(weight) - 1][len(avaible_forwarders) - 1][i]
            index_max = i
    remaining = solution_table[len(weight) - 1][len(avaible_forwarders) - 1][index_max]
    w = index_max
    class_id = len(weight) - 1
    i = len(avaible_forwarders) - 1
    allocated_nodes = dict()
    allocated_bandwidth = dict()
    while remaining > 0:
        if i > 0 and remaining == solution_table[class_id][i-1][w]:
            i = i - 1
        else:
            # The item belongs to the solution
            allocated_nodes[class_id] = weight[class_id][i]
            allocated_bandwidth[class_id] = values[class_id][i]
            # Reduce the weight of the item from the pending total weight
            remaining = remaining - values[class_id][i]
            w = w - weight[class_id][i]
            # Since we can only pick ONE item from each class, move on to the next one
            class_id -= 1
            i = min(w, len(avaible_forwarders) - 1)
            if i == 0:
                i = len(avaible_forwarders) - 1
            if w == 0:
                # In case we do not have more available forwarders, we need to use 0
                i = 0
            #    assert False #we cannot because 0 is no longer an option
    selected_nodes = dict()
    for i, job in enumerate(job_list):
        selected_nodes[job] = allocated_nodes[i]
        # Remember to convert the value back to the floating point
        #expected_bandwith[job] = allocated_bandwidth[i] / 100000.0
    return selected_nodes
