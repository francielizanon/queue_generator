This code was made to generate queues of jobs to be executed during an online experiment where I/O resource decisions will be taken. 

In the current state, the decisions are on the number of I/O nodes to be used by each application. We have a set of 7 applications (see application_encode.py) whose execution time was measured by Jean Bez in the Grid'5000 (Nancy site), and written to the results-runtime.csv file.

