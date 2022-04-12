import numpy as np 

class Solution:

    def __init__(self,J,T):
        
        self.prices = np.empty((J,T))
        self.demand = np.empty((J,T))
        self.productions = np.empty((J,T))
        self.inventories = np.empty((J,T))
        self.setups = np.empty((J,T))
        self.obj = 0

        return 
    
    def compute_demand_j_t(self,p,j,t,instance,demand_form):
        
        if demand_form == 'linear':
            return instance.A[j][t] + np.dot(instance.B[j],self.prices[:,t]) + instance.B[j][j]*(p - self.prices[j][t])

    def compute_demand_t(self,A,B,seasonality_params,prices,t,demand_form):

        if demand_form == "linear" or demand_form == "LINEAR":
            return A[:,t] + np.dot(B,prices)

        elif demand_form == "iso-elastic" or demand_form == "ISO-ELASTIC":
            demand = np.power(prices,B)
            demand = np.prod(demand,axis = 1)
            demand *=  A[:,t]
            demand *= seasonality_params[:,t]
            return demand
     
    def compute_demand(self,J,T,A,B,seasonality_params,prices,demand_form):

        if demand_form == "linear" or demand_form == "LINEAR":
            return A + np.dot(B,prices)

        elif demand_form == "iso-elastic" or demand_form == "ISO-ELASTIC":
            demand = np.empty((J,T),dtype = float)
            for t in range(T):
                demand_t = self.compute_demand_t(A,B,seasonality_params, prices[:,t],t,demand_form)
                demand[:,t] = demand_t
            
            return demand
    
    def compute_inventory(self,J,T):
        
        self.inventories = np.zeros((J,T),dtype = float)
        self.inventories[:,0] = self.productions[:,0] - self.demand[:,0]
        for t in range(1,T):
           self.inventories[:,t] = self.productions[:,t] + self.inventories[:,t-1] - self.demand[:,t] 
           
        return

    def complete_solution(self,instance,demand_form):

        #1. Compute the demand    
        self.demand = self.compute_demand(instance.J,instance.T,instance.A,instance.B,
                                          instance.seasonality_params,self.prices,demand_form)
        #2. Compute the inventory   
        self.compute_inventory(instance.J,instance.T)
         
        return  
    
    def compute_base_objective(self,instance):
   
        #1. Revenue
        revenue = np.sum(np.multiply(self.prices,self.demand))
        
        #2. Production cost
        production_costs = np.sum(np.multiply(self.productions,instance.c))
        
        #3. Inventory cost
        inventory_costs = np.sum(np.multiply(self.inventories,instance.h))
        
        #4. Setups cost
        setups = np.where(self.productions >0,1,0)
        setups_costs = np.sum(np.multiply(instance.a,setups))
        
        #5. Total profit for all the horizon
        self.obj = revenue - production_costs - inventory_costs - setups_costs
     
        return
    