from hmm import closest_point

import numpy as np

from scipy.stats import beta, bernoulli

def probability_of_signal_given_state(signal_strength, state, base_position, max_range):
    closest_x, closest_y = closest_point(state['function'], state['domain'], base_position)
    #Idea: Use measurement position instead of closest_point_in_state
    #Problem: Missing data will cascade through algorithm
    #Solution: Use measurement position if available. Otherwise current solution
    distance_to_state = np.linalg.norm(base_position - np.array([closest_x, closest_y]))
    if signal_strength == 0:
        return bernoulli.pmf(0, max(0, 1 - distance_to_state/max_range))
    else:
        return bernoulli.pmf(1, max(0, 1 - distance_to_state/max_range))*beta.pdf(signal_strength, 2, 5*distance_to_state/max_range)

def probability_of_position_given_state(position, state, variance):
    state_function = state['function']
    state_domain = state['domain']
    closest_x, closest_y = closest_point(state_function, state_domain, position)
    return 1/(np.sqrt(2*np.pi)*variance)*np.exp(-1*np.linalg.norm([position[0] - closest_x, position[1] - closest_y])/(2*variance**2))

def emission_probabilities(position_measurements, gps_variance, signal_measurements, base_positions, base_ranges, state_space):
    ep = np.ones((position_measurements.shape[0], len(state_space)))
    for row, position in enumerate(position_measurements):
        for column, state in enumerate(state_space):
            for i, signal_strength in enumerate(signal_measurements[row, :]):
                ep[row, column] = ep[row, column]*probability_of_signal_given_state(signal_strength, state, base_positions[i], base_ranges[i])
            ep[row, column] = ep[row, column]*probability_of_position_given_state(position, state, gps_variance)
    return ep
                
    #Return, for each observation (vector), find the probability of making 
    #this observation given each state (so observation x state space)
    
    #For each possible state
        #Calculate the probability that one would observe the n signal strengths and
        #the position measurement
        #In the case of missing data, use high-variance with mean measurment, or high-variance with last observation

