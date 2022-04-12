import numpy as np 
from .cmlsp import *

def read_logistics_data(instance,J,T):
    
    """
       # Production costs
    """
    start = 7
    c = np.zeros((J,T))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        c[j] = line_j
 
    start += J + 2
    h = np.zeros((J,T))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        h[j] = line_j
        
    """
       Setup costs
    """
    start += J + 2
    a = np.zeros((J,T))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        a[j] = line_j    
      
    """
       Capacity used
    """
    start += J + 2
    v = np.array(list(map(float,instance[start].split(' ')[:])))

    """
       Production capacity
    """

    start += 3
    prod_cap = np.array(list(map(float,instance[start].split(' ')[:])))
    
    return c, h, a, v, prod_cap, start + 4
    
def read_market_data(instance, J, T, start):
    
    """
      # Prices lower bounds
    """
    lbs = np.zeros((J,T))
    for j in range(J):  
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        lbs[j] = line_j
    
    """
       # Prices upper bounds
    """

    start += J + 2 
    ubs = np.zeros((J,T))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        ubs[j] = line_j
    
    """
       # Demand parameter A
    """
    start += J + 2 
    A = np.zeros((J,T))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        A[j] = line_j
    
    """
       # Demand parameter B
    """
    start += J + 2 
    B = np.zeros((J,J))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        B[j] = line_j
    
    start += J + 2
    seasonality_params = np.zeros((J,T))
    for j in range(J):
        line_j = instance[start + j].split(' ')
        line_j = np.array(list(map(float,line_j)))
        seasonality_params[j] = line_j
    
    return lbs, ubs, A, B,seasonality_params

def from_array_to_dict(J,T,c,h,a):
    
    c_dict = {}
    h_dict = {}
    a_dict = {}

    for j in range(J):
        for t in range(T):
            c_dict[(j+1,t+1)] = c[j][t]
            h_dict[(j+1,t+1)] = h[j][t]
            a_dict[(j+1,t+1)] = a[j][t]
    
    return c_dict,h_dict,a_dict

def read_instance(J,T):

    instance_path = f'./instances/products_{J}_periods_{T}.LDT'
    instance = open(instance_path).read().split('\n')
    J = int(instance[2].split(' ')[0])
    T = int(instance[4].split(' ')[0])
    
    c, h, a, v, prod_cap, start_index = read_logistics_data(instance,J,T)
    lbs, ubs, A, B,seasonality_params = read_market_data(instance, J, T, start_index)
    c_dict,h_dict,a_dict = from_array_to_dict(J,T,c,h,a)
    
    instance = Cmlsp(J,T,c,h,a,v,prod_cap,lbs, 
                    c_dict,h_dict,a_dict,ubs, 
                    A,B,seasonality_params)

    return instance