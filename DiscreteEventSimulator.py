from math import log,e
from numpy.random import uniform
from numpy import array, vectorize
import heapq

from enum import Enum

NUM_SAMPLE = 1000

class DiscreteEventSimulator:


    class EventType(Enum):
        ARRIVAL = 1
        DEPARTURE = 2
        OBSERVER = 3


    class Event:
        def __init__(self):
            self.event_type = None
            self.nominal_sim_time = None # used for sorting events

    class ArrivalEvent(Event):

        def __init__(self, arrival_time, packet_length=None, service_time=None):
            super().__init__()
            # should we add a flag to check if arrival packet is dropped or not?? @drew
            self.arrival_time = arrival_time
            self.packet_length = packet_length
            self.service_time = service_time

            self.event_type = self.EventType.ARRIVAL

            self.nominal_sim_time = arrival_time

    class DepartureEvent(Event):

        def __init__(self, departure_time, transmission_time=None, is_queue_idle=None, packet_length=None):
            super().__init__()
            self.departure_time = departure_time
            self.transmission_time = transmission_time
            self.is_queue_idle = is_queue_idle
            self.packet_length = packet_length

            self.event_type = self.EventType.DEPARTURE

            self.nominal_sim_time = departure_time

    class ObserverEvent(Event):
        
        def __init__(self, observer_time, time_average_packets=None, average_packets_in_queue=None, proportion_idle=None, proportion_loss=None):
            super().__init__()
            self.time_average_packets = time_average_packets
            self.average_packets_in_queue = average_packets_in_queue
            self.proportion_idle = proportion_idle
            self.proportion_loss = proportion_loss

            self.event_type = self.EventType.OBSERVER

            self.nominal_sim_time = observer_time

            
    class Packet:
        def __init__(self, packet_id, packet_length, packet_arrival_time, packet_departure_time):
        
            self.packet_id = packet_id
            self.packet_length = packet_length
            self.packet_arrival_time = packet_arrival_time
            self.packet_departure_time = packet_departure_time


    class EventSheet:
        def __init__(self) -> None:
            self.observations = []

        def print_observations(self):
            pass

        def append(evet):
            pass

    def __init__(self, rate):

        self.rate = rate

        self.number_of_packet_arrivals = 0
        self.number_of_packet_departures = 0
        self.number_of_packet_observations = 0
        self.number_of_dropped_packets = 0
        self.previous_departure_time = 0

        self.future_events_heap = []
        self.network_queue = []

        # generate our incoming packet events 

        arrival_times = simulateExponential(rate).sort()
        arrival_events = [ self.ArrivalEvent(arrival_time=x) for x in arrival_times]

        # generate observer events 5*rate 

        observer_times = simulateExponential(5*rate).sort()
        observer_events = [ self.ObserverEvent(observer_time=x) for x in observer_times]

        # we will not be able to use the future_events_heap as python does
        # not allow this - we will have to use the compare the observer_times, 
        # arrival_times, and departure times and pick the min of the three






def simulateExponential(rate):
    # rate must be bigger than 0
    if rate <= 0:
        return []
    # natural logarithm
    def _ln(x):
        return log(x,e)
    
    # generate NUM_SMAPLE points from uniform distribution
    U = array(uniform(low=0.0, high=1.0, size=NUM_SAMPLE))

    # vectorize ln function to apply to numpy array
    _vln = vectorize(_ln)

    # return numpy array of NUM_SAMPLE points using formula outlined in doc
    return array(-(1/rate)*_vln(1-U))
    
    

exp75 = simulateExponential(75)
print(exp75.mean(), exp75.var())


