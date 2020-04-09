This code was made to generate queues of jobs to be executed during an online experiment where I/O resource decisions will be taken. It was written in Python3 and uses numpy.

In the current state, the decisions are on the number of I/O nodes to be used by each application. We have a set of applications (see application_encode.py) whose execution time was measured by Jean Bez in the Grid'5000 (Nancy site), and written to the results-runtime.csv file.

Parameters are given directly into the generate_queues.py file, which upon execution will generate an output file with one queue and its metrics per line. The queue is encoded with one letter per job. For details, see application_encode.py

There is no guarantee the code will always stop and find a solution, specially as we pile up filters and increase the number of generated queues (we might reach a situation where there are not enough possible queues). However, that is highly unlikely.

# How to add new applications

- The execution time of that application with different numbers of I/O nodes must be listed in the results-runtime.csv file

- The combination of application name, number of nodes and number of processes MUST uniquely identify that application (the whole code works on that assumption)

- Update application_encode.py to assign a letter to the new applications

- Make sure bandwidth.py is able to find the bandwidth for the new applications with different numbers of I/O nodes

# How to filter the generated queues

- At the end of the generate_queues.py file, in the while loop where the queues are generated, before encoding and adding them to the random_queue list, we can check its metrics and choose to skip if they are not as we want them. For details on the metrics available, see the documentation for the Queue and Metrics classes.

# Known issues

Sometimes (it is quite rare), because of floating number precision issues, the end time of a job during the simulation will decrease after updating the clock and re-calculating it. The problem with that is that when we have multiple jobs with end times that are very close, we may have clock updates that do not change its value, and then the policy will be called twice for the same clock. That will artificially decrease the median_period and mean_period metrics and increase policy_calls. Still, it is quite rare (like once every 1000 queues), and these metrics are estimations anyway. Still, when that happens the code prints a "PANIC" message to the terminal, so repeating it a few times should be enough to get a set of queues without this occurrence. 

# TO DO

- Bandwidth in bandwidth.py
- confirm line 59 of policy.py (in the MCKP implementation) is not an error
