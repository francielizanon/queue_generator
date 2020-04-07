This code was made to generate queues of jobs to be executed during an online experiment where I/O resource decisions will be taken. 

In the current state, the decisions are on the number of I/O nodes to be used by each application. We have a set of 7 applications (see application_encode.py) whose execution time was measured by Jean Bez in the Grid'5000 (Nancy site), and written to the results-runtime.csv file.

The code outputs an error message from numpy but it does not seem to affect the execution, so I did not further investigate it.

Parameters are given directly into the generate_queues.py file, which upon execution will generate an output file with one queue and its metrics per line. The queue is encoded with one letter per job. For details, see application_encode.py

In the while loop at the end of the generate_queues.py file, additional filters may be added to keep only queues that have some potential. 

There is no guarantee the code will always stop and find a solution, specially as we pile up filters and increase the number of generated queues (we might reach a situation where there are not enough possible queues). However, that is very unlikely.
