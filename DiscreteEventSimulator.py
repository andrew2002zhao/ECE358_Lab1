from math import log,e
import numpy as np
from numpy.random import uniform
from numpy import array, vectorize
import heapq

from enum import Enum

NUM_SAMPLE = 1000
AVERAGE_LENGTH = 2000

class DiscreteEventSimulator:
    
  

    class Event:
        class EventType(Enum):
            ARRIVAL = 1
            DEPARTURE = 2
            OBSERVER = 3
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

            self.event_type = self.EventType.ARRIVAL.name

            self.nominal_sim_time = arrival_time

    class DepartureEvent(Event):

        def __init__(self, departure_time, transmission_time=None, is_queue_idle=None, packet_length=None):
            super().__init__()
            self.departure_time = departure_time
            self.transmission_time = transmission_time
            self.is_queue_idle = is_queue_idle
            self.packet_length = packet_length

            self.event_type = self.EventType.DEPARTURE.name

            self.nominal_sim_time = departure_time

    class ObserverEvent(Event):
        
        def __init__(self, observer_time, time_average_packets=None, average_packets_in_queue=None, proportion_idle=None, proportion_loss=None):
            super().__init__()
            self.time_average_packets = time_average_packets
            self.average_packets_in_queue = average_packets_in_queue
            self.proportion_idle = proportion_idle
            self.proportion_loss = proportion_loss

            self.event_type = self.EventType.OBSERVER.name

            self.nominal_sim_time = observer_time

            
    class Packet:
        def __init__(self, packet_id, packet_length, packet_arrival_time, packet_departure_time):
        
            self.packet_id = packet_id
            self.packet_length = packet_length
            self.packet_arrival_time = packet_arrival_time
            self.packet_departure_time = packet_departure_time
    
 
    class Queue:
        def __init__(self, sim_time, is_finite=False, capacity=None):
            # if is_finite set to True then capacity cannot be none - M/M/K queue
            self.is_finite = is_finite
            self.capacity = capacity


            self.packet_queue = []
            self.packet_counter = 0 # to help with determining E[N]
            self.sim_time = sim_time
            self.queue_empty_time = 0

            self.start_duration = 0
            self.end_duration = 0

            # E[N] - have a running sum of number of packets in the queue then divide by total 
            #        simulation time 

        # packet arrival - add packet to queue
        def add_packet(self, packet, nominal_sim_time):
            
            # logic to determine queue empty time
            if self.is_queue_empty():
                self.end_duration = nominal_sim_time
           

            self.packet_queue.append(packet)
            self.packet_counter = self.packet_counter + 1

        # service packet - remove packet from top of queue to be serviced
        def remove_packet(self, nominal_sim_time):
            if not self.is_queue_empty():
                
                # logic to determine queue empty time
                if self.packet_queue.count() == 1:
                    self.start_duration = nominal_sim_time

                return self.packet_queue.pop(SupportsIndex=0)
            
            
        def is_queue_empty(self):
            return  True if self.packet_queue.count <= 0 else False
        
        def queue_observe(self, nominal_sim_time):
            # observe elements in the queue
            # average number of packets in queue, and time queue is empty
            
            return self._running_time_average(nominal_sim_time), self.is_queue_empty()
        

        def _running_time_average(self, nominal_sim_time):
            return float(self.packet_counter/nominal_sim_time)
        
        def _running_time_queue_empty(self):
            pass
        # create is full function for M/M/K queue - compare capacity to queue count



    class EventSheet:
        def __init__(self) -> None:
            self.observations = []

        def print_observations(self):
            pass

        def append(evet):
            pass

    def __init__(self, rate, transmission_speed, buffer_size=0):

        self.rate = rate
        self.transmission_speed = transmission_speed
        self.buffer_size = buffer_size
        

        self.number_of_packet_arrivals = 0
        self.number_of_packet_departures = 0
        self.number_of_packet_observations = 0
        self.number_of_dropped_packets = 0

        self.network_queue = []
        self.number_of_items = 0
        self.empty_queue = True
        self.full_queue = False

        # generate our incoming packet events 

        arrival_times = self.simulateExponential(rate)
        # @orson we need a prefix sum here not the base time
        arrival_times = np.cumsum(arrival_times)
        self.arrival_events = [ self.ArrivalEvent(arrival_time=x) for x in arrival_times]
        
        # generate observer events 5*rate 

        observer_times = self.simulateExponential(5*rate)
        # @orson we need a prefix sum here not the base time
        observer_times = np.cumsum(observer_times)
        self.observer_events = [ self.ObserverEvent(observer_time=x) for x in observer_times]

        # we will not be able to use the future_events_heap as python does
        # not allow this - we will have to use the compare the observer_times, 
        # arrival_times, and departure times and pick the min of the three
    
   
  
    def simulateExponential(self, rate):
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
    
    def getPacketLength(self, average_length=AVERAGE_LENGTH):
        
        if average_length <= 0.0:
            return 0.0 # print error statement
        else:
            rate = float(1/average_length) # scale parameter conversion to rate parameter
        
        def _ln(x):
            return log(x, e)
        
        U = uniform(low=0.0, high=1.0, size=1)

        result = float(-(1/rate)*_ln(1-U))
        print("exponentially distributed packet length:", result)
        return result
        
    # is_finite to determine if we are using M/M/K or M/M/1 queue
    def runSimulation(self, t_seconds, is_finite=False):



        def getNextEvent(arrivalEvent, observerEvent, departureEvent):
            # put events in event recorder
            if(arrivalEvent.nominal_sim_time < observerEvent.nominal_sim_time and arrivalEvent.nominal_sim_time < departureEvent.nominal_sim_time):
                return arrivalEvent
            if(observerEvent.nominal_sim_time < departureEvent.nominal_sim_time):
                return observerEvent
            return departureEvent
        
        for x in range(5):
            max_simulation_time = x * t_seconds
            # make queue empty
            self.network_queue = []
            # initialize all events and times
            null_departure_event = self.DepartureEvent(max_simulation_time)
            departure_event = null_departure_event
            arrival_event_pointer = 0
            observer_event_pointer = 0
            simulation_time = 0
            
            # instantiate new Queue class - use M/M/1 or M/M/K queue depending on is_finite
            packet_queue = self.Queue(x*t_seconds) if not is_finite else self.Queue(sim_time = x*t_seconds,is_finite=True, capacity=1000)

            while simulation_time < max_simulation_time:
                # get next event to run
                next_event = getNextEvent(
                                self.arrival_events[arrival_event_pointer],
                                self.observer_events[observer_event_pointer],
                                departure_event
                            )
                                
                if(isinstance(next_event, self.ArrivalEvent)):
                    # we have an arrival event
                    print("Arrival Event")
                    packet_arrival(packet_queue, self.getPacketLength())
                    arrival_event_pointer += 1
                    simulation_time += 1 #andrew shouldn't we augment simulation time by the event.nominal_sim_time ???
                elif(isinstance(next_event, self.ObserverEvent)):
                    print("observer event")
                    observe_queue(packet_queue, next_event.nominal_sim_time)
                    observer_event_pointer += 1
                    simulation_time += 1
                elif(isinstance(next_event, self.DepartureEvent)):
                    print("departure event")
                    packet_departure(packet_queue)
                    simulation_time += 1

            print("arrival_events", arrival_event_pointer, "observer_events", observer_event_pointer)






    
discreteEventSimulator = DiscreteEventSimulator(75, 100)
discreteEventSimulator.runSimulation(100)
discreteEventSimulator.getPacketLength()

# exp75 = simulateExponential(75)
# print(exp75)
# print(exp75.mean(), exp75.var())


