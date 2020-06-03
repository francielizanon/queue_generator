import os
import csv
import pprint

from application import Application
from application_encode import encode_application


class Bandwidth():
    """
    Used to access the bandwidth estimations for applications
    with different numbers of I/O nodes
    """

    DB_BANDWIDTH_FILE = 'bandwidth.csv'

    def __init__(self):
        """Load the database of access patterns and performance metrics."""

        self.bandwidth = {}

        if not os.path.isfile(self.DB_BANDWIDTH_FILE):
            print('unable to find the bandwidth database file')

            exit()

        with open(self.DB_BANDWIDTH_FILE, 'r') as csv_file:
            rows = csv.DictReader(csv_file, delimiter=';')

            for row in rows:
                if row['scenario'] not in self.bandwidth:
                    self.bandwidth[row['scenario']] = dict()

                if row['clients'] not in self.bandwidth[row['scenario']]:
                    self.bandwidth[row['scenario']][row['clients']] = dict()

                if row['processes'] not in self.bandwidth[row['scenario']][row['clients']]:
                    self.bandwidth[row['scenario']][row['clients']][row['processes']] = dict()

                if row['forwarders'] not in self.bandwidth[row['scenario']][row['clients']][row['processes']]:
                    self.bandwidth[row['scenario']][row['clients']][row['processes']][row['forwarders']] = float(row['bandwidth'])

        print('loaded database of bandwidths')
    
    def get(self, app, nodes, procs, ion):
        """ 
        given the name of the application app (as in the 
        results-runtime.csv file, the number of nodes, the
        number of processes procs, and the number of I/O nodes
        ion, retuns the bandwidth
        """
        #we need to pass the same structe to the encode application function
        application = Application(app, nodes, procs, False)
        #print("->", encode_application(application))

        #pprint.pprint(self.bandwidth)
        try:
            return self.bandwidth[encode_application(application)][str(nodes)][str(procs)][str(ion)]
        except KeyError as e:
            print('unable to find the bandwidth for: {} ({}) {} {} {}'.format(app, encode_application(application), nodes, procs, ion))

            exit()
