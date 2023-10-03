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
        def __init__(self, is_finite=False, capacity=None):
            # if is_finite set to True then capacity cannot be none - M/M/K queue
            self.is_finite = is_finite

            # set capacity to none if M/M/K queue 
            self.capacity = capacity


            self.packet_queue = []
            self.packet_counter = 0 # to help with determining E[N]
            self.queue_empty_count = 0
            self.packet_observer_count = 0

            self.start_duration = 0
            self.end_duration = 0

            # PLoss counter - count the number of packets that are dropped if queue size > cap
            self.dropped_packet = None if is_finite else 0

            # E[N] - have a running sum of number of packets in the queue then divide by total 
            #        simulation time 

        # packet arrival - add packet to queue
        def add_packet(self, packet):

            # if queue is M/M/K and if the queue is full increment dropped packet counter
            if self.is_finite and self.capacity > 0:
                if len(self.packet_queue) == self.capacity:
                    self.dropped_packet = self.dropped_packet + 1
                    self.packet_counter = self.packet_counter + 1 # still need to increment this to compute the droped packets over TOTAL number of packets wanting to be sent 
                    return 

            
           

            self.packet_queue.append(packet)
            self.packet_counter = self.packet_counter + 1

        # service packet - remove packet from top of queue to be serviced
        def remove_packet(self):
            if not self.is_queue_empty():               

                packet_to_return = self.packet_queue[0]
                del self.packet_queue[0]

                return packet_to_return # maybe use a deque here 
            
            
        def is_queue_empty(self):
            return  True if len(self.packet_queue) <= 0 else False
        
        def queue_observe(self, observer_event_count):
            # observe elements in the queue
            # average number of packets in queue over current duration of nominal_sim_time, 
            # and time queue is empty over current duration of nominal_sim_time, and Packet dropped ratio
            return self._running_time_average(observer_event_count), self._running_queue_empty(observer_event_count), self._running_dropped_packet_ratio(), 1-self._running_queue_empty(observer_event_count)
        

        # returns the current running time average of elements in the queue
        def _running_time_average(self, observer_event_count):
            
            self.packet_observer_count = self.packet_observer_count + len(self.packet_queue)
            return float(self.packet_observer_count/observer_event_count)
        
        # returns the current running Pidle 
        def _running_queue_empty(self, observer_event_count):
            
            self.queue_empty_count = self.queue_empty_count + 1 if self.is_queue_empty() else self.queue_empty_count
            return float(self.queue_empty_count/observer_event_count)
        
        # compute packet dropped ratio using dropped packets and total number of packets sent
        def _running_dropped_packet_ratio(self):
            # if queue is M/M/1 then return None
            if not self.is_finite:
                return None
            else:
                return float(self.dropped_packet/self.packet_counter)



    class EventSheet:
        def __init__(self):
            self.observations = []

        def print_observations(self):
            pass

        def append(self, event):
            pass

    def __init__(self, rate, transmission_speed, sim_time=100, buffer_size=0):

        self.rate = rate
        self.transmission_speed = transmission_speed
        self.buffer_size = buffer_size
        self.sim_time = sim_time

        self.number_of_packet_arrivals = 0
        self.number_of_packet_departures = 0
        self.number_of_packet_observations = 0
        self.number_of_dropped_packets = 0

        self.network_queue = []
        self.number_of_items = 0
        self.empty_queue = True
        self.full_queue = False

        self.arrival_events = []
        self.observer_events = []

        # generate our incoming packet events 

        #arrival_times = self.simulateExponential(rate)
        # @orson we need a prefix sum here not the base time
        #arrival_times = np.cumsum(arrival_times)
        #self.arrival_events = [ self.ArrivalEvent(arrival_time=x) for x in arrival_times]

        #generate arrival events
        arrival_events_sum = 0
        while arrival_events_sum < self.sim_time:
            
            time = self.getExponential(rate=rate)
            arrival_events_sum += time
            self.arrival_events.append(self.ArrivalEvent(arrival_time=time))

        # generate observer events 5*rate        
        observer_events_sum = 0
        while observer_events_sum < self.sim_time:
            
            time = self.getExponential(rate=5*rate)
            observer_events_sum += time
            self.observer_events.append(self.ObserverEvent(observer_time=time))


        #observer_times = self.simulateExponential(5*rate)
        # @orson we need a prefix sum here not the base time
        #observer_times = np.cumsum(observer_times)
        #self.observer_events = [ self.ObserverEvent(observer_time=x) for x in observer_times]

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

    def getExponential(self, rate=1000):
        
        if rate <= 0.0:
            return 0.0 # print error statement
        
        def _ln(x):
            return log(x, e)
        
        U = uniform(low=0.0, high=1.0, size=1)

        result = float(-(1/rate)*_ln(1-U))
        return result
    
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
    def runSimulation(self, is_finite=False, capacity=None, transmission_rate=10e6):
        
        def getNextEvent(arrivalEvent, observerEvent, departureEvent):
            # Andrew put events in event recorder - to just log events - super simple task 
            # add

            if(arrivalEvent.nominal_sim_time < observerEvent.nominal_sim_time and arrivalEvent.nominal_sim_time < departureEvent.nominal_sim_time):
                return arrivalEvent
            if(observerEvent.nominal_sim_time < departureEvent.nominal_sim_time):
                return observerEvent
            return departureEvent
        
        for x in range(5):
            max_simulation_time = x * self.sim_time
            # make queue empty
            self.network_queue = []
            # initialize all events and times
            null_departure_event = self.DepartureEvent(max_simulation_time)
            departure_event = null_departure_event
            arrival_event_pointer = 0
            observer_event_pointer = 0
            simulation_time = 0

            departure_event_queue = []
            departure_event_pointer = 0
            
            # instantiate new Queue class - use M/M/1 or M/M/K queue depending on is_finite
            packet_queue = self.Queue() if not is_finite else self.Queue(is_finite=True, capacity=capacity)

            while simulation_time < max_simulation_time:

                # get packet to be transmitted 
                packet = self.getPacketLength()

                # need to dynamically generate departure_events either based on arrivals or previous departures
                #############################################################################################
                if packet_queue.is_queue_empty():
                    # current arrival time + L/R
                    d_event = self.DepartureEvent(departure_time=float(self.arrival_events[arrival_event_pointer].arrival_time + float(packet/transmission_rate)))
                    departure_event_queue.append(d_event)
                else:
                    # last element add to queue + L/R
                    # Andrew can we ever reach the case where there is nothing in the departure queue?
                    d_event = self.DepartureEvent(departure_time=float(departure_event_queue[-1].departure_time + float(packet/transmission_rate)))
                    departure_event_queue.append(d_event)
                #############################################################################################
                
                # get next event 
                next_event = getNextEvent(
                                self.arrival_events[arrival_event_pointer],
                                self.observer_events[observer_event_pointer],
                                departure_event_queue[departure_event_pointer]
                            )
                                
                if(isinstance(next_event, self.ArrivalEvent)):
                    # we have an arrival event
                    print("Arrival Event")
                    # add packet to the queue
                    packet_queue.add_packet(packet=packet)
                    arrival_event_pointer = arrival_event_pointer + 1 if arrival_event_pointer < len(self.arrival_events)-1 else arrival_event_pointer
                    simulation_time = next_event.nominal_sim_time 
                elif(isinstance(next_event, self.ObserverEvent)):
                    print("observer event")
                    # get queue statistics - this will be used to help us graph
                    E_n, P_i, P_l, rho = packet_queue.queue_observe(observer_event_count=observer_event_pointer)
                    print("E[N]: {}, P_idle: {}, P_loss: {}, rho: {}".format(E_n, P_i, P_l, rho))
                    observer_event_pointer = observer_event_pointer + 1 if observer_event_pointer < len(self.observer_events)-1 else observer_event_pointer
                    simulation_time = next_event.nominal_sim_time
                elif(isinstance(next_event, self.DepartureEvent)):
                    print("departure event")
                    # remove packet from queue
                    packet_queue.remove_packet()
                    departure_event_pointer = departure_event_pointer + 1 if departure_event_pointer < len(departure_event_queue)-1 else departure_event_pointer
                    simulation_time = next_event.nominal_sim_time

            print("arrival_events", arrival_event_pointer, "observer_events", observer_event_pointer)




# def(p):
#     

    
discreteEventSimulator = DiscreteEventSimulator(75, 100)
discreteEventSimulator.runSimulation()
discreteEventSimulator.getPacketLength()

# exp75 = simulateExponential(75)
# print(exp75)
# print(exp75.mean(), exp75.var())


