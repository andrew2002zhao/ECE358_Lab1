from math import log,e
from numpy.random import uniform
from numpy import array, vectorize
import heapq

from enum import Enum

NUM_SAMPLE = 1000

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
        self.arrival_events = [ self.ArrivalEvent(arrival_time=x) for x in arrival_times]

        # generate observer events 5*rate 

        observer_times = self.simulateExponential(5*rate)
        # @orson we need a prefix sum here not the base time
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
    

    
        
        
    def runSimulation(self, t_seconds):
        def getNextEvent(arrivalEvent, observerEvent, departureEvent):
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
                    arrival_event_pointer += 1
                    simulation_time += 1
                elif(isinstance(next_event, self.ObserverEvent)):
                    print("observer event")
                    observer_event_pointer += 1
                    simulation_time += 1
                elif(isinstance(next_event, self.DepartureEvent)):
                    print("departure event")
                    simulation_time += 1

        






    
discreteEventSimulator = DiscreteEventSimulator(75, 100)
discreteEventSimulator.runSimulation(100)

# exp75 = simulateExponential(75)
# print(exp75)
# print(exp75.mean(), exp75.var())


