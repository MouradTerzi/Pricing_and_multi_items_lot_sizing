import sys 
import random 
import copy 

from .solution import *
from exact_solvers.exact_solver import * 
from utils.checker import *

class Solution_sa_prices(Solution):
    
    def __init__(self,J,T):
        super().__init__(J,T)
        self.ex_sol = EXACT_SOLVER()
        self.checker = Checker()
        return

    def generate_random_solution_cmlsp_resolution(self,instance,demand_form):
        
        #1. Generate the prices randomly
        prices = np.empty((instance.J,instance.T),dtype = float)
        demand = np.empty((instance.J,instance.T),dtype = float)
        prices_t = np.empty(instance.J,dtype = float)
        demand_t = np.empty(instance.J,dtype = float)
        t,cum_cap,cum_demand = 0,0,0
        while t < instance.T:
            prices_t = np.array([random.uniform(instance.lbs[j][t], instance.ubs[j][t]) for j in range(instance.J)])
            demand_t = self.compute_demand_t(instance.A, instance.B, instance.seasonality_params, prices_t,t,demand_form)
            
            cap_for_demand_t = np.dot(instance.v,demand_t)
            if (cum_cap + instance.prod_cap[t]) >= (cum_demand + cap_for_demand_t):
                prices[:,t] = prices_t
                demand[:,t] = demand_t
                cum_cap += instance.prod_cap[t]
                cum_demand += cap_for_demand_t
                t+=1
                prices_t = np.ones(instance.J,dtype = float)
            
        #2. Resolve the capacitated multi item lot sizing problem resulted from the generated demand 
        ex_sol = EXACT_SOLVER()
        setups,productions,inventories,obj = ex_sol.cmlsp_resolution(instance.J,instance.T,demand,
                                                                     instance.c_dict,instance.h_dict,
                                                                     instance.a_dict,instance.v,instance.prod_cap)
        self.productions = productions
        self.inventories = inventories
        self.prices = prices
        self.demand = demand
        self.compute_base_objective(instance)

        return 
    """
       # Generate neighbors solution for X-P coding
    """
    def generate_neighbors_solution(self,instance,demand_form,wn1):

        r = random.uniform(0,1)
        if r <= 0.5:
            self.generate_neighbors_solution_products(instance,demand_form)
        
        else:
            self.generate_neighbors_solution_periods(instance,demand_form)
        
        return 
    
    def generate_neighbors_solution_products(self,instance,demand_form):
        
        products = [j for j in range(instance.J)]
        while len(products) > 0:
            j = random.choice(products)
            generated = self.generate_neighbors_solution_single_product(instance,j,demand_form)
            if generated != 1:
                products.remove(j)
            
            else:
                break

        return 

    def generate_neighbors_solution_single_product(self,instance,j,demand_form):
     
        alpha = 0.2
        current_prices = copy.deepcopy(self.prices[j])
        while alpha <= 0.8:
            new_prices = np.array([random.uniform((1-alpha)*self.prices[j][t],(1+alpha)*self.prices[j][t]) \
            for t in range(instance.T)])

            new_prices = np.where(new_prices < instance.lbs[j],instance.lbs[j],new_prices)
            new_prices = np.where(new_prices > instance.ubs[j],instance.ubs[j],new_prices)
            self.prices[j] = copy.deepcopy(new_prices)

            demand = self.compute_demand(instance.J,instance.T,instance.A,instance.B,
                                         instance.seasonality_params,self.prices,demand_form)

            feasible = self.checker.check_feasible_demand(instance.T,instance.v,instance.prod_cap,demand)
            if feasible == 1:
                setups,productions, inventories,obj = self.ex_sol.cmlsp_resolution(instance.J,instance.T,demand,
                                                                                   instance.c_dict,instance.h_dict,
                                                                                   instance.a_dict,instance.v,
                                                                                   instance.prod_cap)
                if obj != -1:
                    self.productions = productions
                    self.inventories = inventories
                    self.demand = demand
                    self.compute_base_objective(instance)
                    
                    return 1
                
                else:
                    alpha += 0.2
                    self.prices[j] = copy.deepcopy(current_prices)
                
            else:
               alpha += 0.2
               self.prices[j] = copy.deepcopy(current_prices)

        return 0
    
    def generate_neighbors_solution_periods(self,instance,demand_form):
        
        periods = [t for t in range(instance.T)]
        alpha = 0.05
        while len(periods) > 0:
            t = random.choice(periods)
            generated = self.generate_neighbors_solution_single_period(instance,t,demand_form)
            if generated != 1:
                periods.remove(t)
            
            else:
                break

        return 
    
    def generate_neighbors_solution_single_period(self,instance,t,demand_form):

        alpha = 0.2
        current_prices = copy.deepcopy(self.prices[:,t])
        
        while alpha <= 0.8:
            new_prices = np.array([random.uniform((1-alpha)*self.prices[j][t],(1+alpha)*self.prices[j][t]) \
            for j in range(instance.J)])

            new_prices = np.where(new_prices < instance.lbs[:,t],instance.lbs[:,t],new_prices)
            new_prices = np.where(new_prices > instance.ubs[:,t],instance.ubs[:,t],new_prices)
            self.prices[:,t] = copy.deepcopy(new_prices)

            demand = self.compute_demand(instance.J,instance.T,instance.A,instance.B,
                                         instance.seasonality_params,self.prices,demand_form)

            feasible = self.checker.check_feasible_demand(instance.T,instance.v,instance.prod_cap,demand)
            if feasible == 1:
                setups,productions, inventories,obj = self.ex_sol.cmlsp_resolution(instance.J,instance.T,demand,
                                                                                   instance.c_dict,instance.h_dict,
                                                                                   instance.a_dict,instance.v,
                                                                                   instance.prod_cap)                                 
                if obj != -1:
                    self.productions = productions
                    self.inventories = inventories
                    self.demand = demand
                    self.compute_base_objective(instance)
                    
                    return 1
                
                else:
                    alpha += 0.2
                    self.prices[:,t] = copy.deepcopy(current_prices)
                
            else:
               alpha += 0.2
               self.prices[:,t] = copy.deepcopy(current_prices)

        return 0
    