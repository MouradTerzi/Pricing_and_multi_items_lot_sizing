import numpy as np 

class Checker:

    def check_solution_is_true(self,solution,instance,demand_form):
     
        #Demand 
        if demand_form == 'linear':
            demand = instance.A + np.dot(instance.B,self.prices)
        
        print('computed demand\n',demand)
        print('new demand\n',self.demand)

        #Inventories 
        inventories = np.zeros((instance.J,instance.T))
        inventories[:,0] = solution.productions[:,0] - demand[:,0]
        
        for t in range(1,instance.T):
           inventories[:,t] = solution.productions[:,t] + inventories[:,t-1] - demand[:,t] 

        print(solution.demand == demand)        
        print(solution.inventories == inventories)

        return

    def check_feasibility(self,solution,instance):
    
        vc,vc_indexes = self.check_violation_of_production_capacity(solution.productions,
                                                                     instance.v,instance.prod_cap)
        nd,nd_indexes = self.check_negative_demand(solution.demand)
        ni,ni_indexes = self.check_negative_inventory(solution.inventories)
        ei,ei_indexes = self.check_excess_inventory(solution.inventories[:,instance.T-1])
        lbs_v,lbs_violation_indexes = self.check_lbs_violation(solution.prices,instance.lbs)
        ubs_v,ubs_violation_indexes = self.check_ubs_violation(solution.prices,instance.ubs)

        return vc, nd, ni, ei
     
    def check_violation_of_production_capacity(self,productions,v,prod_cap):
        
        used_capacity = np.dot(v,solution.productions)
        violated_capacity = np.where(100*(used_capacity - prod_cap)/prod_cap > 0,100*(used_capacity - prod_cap)/prod_cap,0)
        violated_capacity = np.around(violated_capacity,decimals = 1)
        
        vc_indexes = np.where(violated_capacity > 0)[0]
        if len(vc_indexes) > 0:
            return 1, vc_indexes
        
        else:
            return 0, np.array([])
           
    def check_negative_demand(self,demand):
        
        negative_demand = np.where(self.demand < 0)
        if len(negative_demand[0]) > 0:
            return 1,np.array(list(zip(negative_demand[0], negative_demand[1])))
        else:
            return 0, np.array([]) 
              
    def check_negative_inventory(self,inventories):
        
        inventories = np.around(inventories,decimals = 1)
        negative_inventory = np.where(inventories < epsilon)
        if len(negative_inventory[0]) > 0:
            return 1, np.array(list(zip(negative_inventory[0], negative_inventory[1])))
        
        else:
            return 0, np.array([])
    
    def check_excess_inventory(self,inventories_T):
        
        ei_indexes = np.where(inventories_T > 0)
        if len(ei_indexes[0]) > 0:
            return 1, ei_indexes[0]
        
        else:
            return 0, np.array([])
         
    def check_lbs_violation(self,prices,lbs):

        lbs_violation = np.where(prices - lbs < 0)
        if len(lbs_violation[0]) > 0:
            return 1, np.array(list(zip(lbs_violation[0], lbs_violation[1])))
        
        else:
            return 0, np.array([])
    
    def check_ubs_violation(self,prices,ubs):

        ubs_violation = np.where(prices - ubs > 0)
        if len(ubs_violation[0]) > 0:
            return 1, np.array(list(zip(ubs_violation[0], ubs_violation[1])))
        
        else:
            return 0, np.array([]) 
    
    def check_feasible_demand(self,T,v,prod_cap,demand):

        cum_cap,cum_demand,t = 0,0,0
        while t < T:
            cap_for_demand_t = np.dot(v,demand[:,t])
            if (cum_demand + cap_for_demand_t) > (cum_cap + prod_cap[t]):
               return 0
            
            else:
                cum_demand += cap_for_demand_t
                cum_cap += prod_cap[t]
                t+=1
        
        return 1
  
   
    
   
   