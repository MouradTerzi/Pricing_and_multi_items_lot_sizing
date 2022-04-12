import random 
import copy
import numpy as np 

from .solution import *
from exact_solvers.nlp_models_creation import *
from utils.solutions_reader_writer import *

class Solution_vns_setups(Solution):
    
    def __init__(self,J,T):
        super().__init__(J,T)
        self.solutions_reader_writer = Solutions_reader_writer()
        return
    
    def generate_prices_lot_sizing_nlp_resolution(self,J,T,setups_costs):
        
        #1. Generate randomly Y vector 
        self.setups = np.array([[random.choice([0,1]) for t in range(T)] for j in range(J)])
        self.setups[:,0] = np.ones(J)
        print(self.setups)

        #2. Ceate the nlp for prices and lot-sizing 
        create_lingo_ltf_file(J,T,self.setups)

        #3 Solve the nlp for prices and lot-sizing
        os.system(f'runlingo nlp_model_J_{J}_T_{T}.ltf')

        productions,inventories,prices,demand,obj = self.solutions_reader_writer.read_setups_solution(J,T,setups_costs)
        self.productions = productions
        self.inventories = inventories
        self.prices = prices
        self.demand = demand
        self.obj = obj
        
        return

    def product_period_neighborhood_exploration(self,J,T,best_improve,setups_costs):

        #1. Consider only (j,t) for which X-D < 0
        indexes = np.where(self.productions - self.demand < 0)
        neighbors_list = [(j,t) for (j,t) in zip(indexes[0],indexes[1])]
        best_j,best_t = -1,-1
        while len(neighbors_list) > 0:
            j,t = neighbors_list[0]
            self.setups[j][t] = 1 - self.setups[j][t]
            create_lingo_ltf_file(J,T,self.setups)
            os.system(f'runlingo nlp_model_J_{J}_T_{T}.ltf')
            productions,inventories,prices,demand,obj = self.solutions_reader_writer.read_setups_solution(J,T,setups_costs)
            
            if obj > self.obj:
                best_productions = copy.deepcopy(productions)
                best_inventories = copy.deepcopy(inventories)
                best_prices = copy.deepcopy(prices)
                best_demand = copy.deepcopy(demand)
                best_obj = obj
                best_j,best_t = j,t
                if best_improve == 0:
                    break
            
            del neighbors_list[0]
            self.setups[j][t] = 1 - self.setups[j][t]
        
        if best_j != -1:
            self.update_current_solution(best_productions,best_inventories,best_prices,
                                         best_demand,best_j,best_t,best_obj)
            return 1

        return 0 
    
    def product_neighborhood_exploration(self,J,T,best_improve,setups_costs):

        neighbors_list = [j for j in range(J)]
        best_j = -1
        while len(neighbors_list) > 0:
            j = neighbors_list[0]
            self.setups[j] = 1 - self.setups[j]
            create_lingo_ltf_file(J,T,self.setups)
            os.system(f'runlingo nlp_model_J_{J}_T_{T}.ltf')
            productions,inventories,prices,demand,obj = self.solutions_reader_writer.read_setups_solution(J,T,setups_costs)
            if obj > self.obj:
                best_productions = copy.deepcopy(productions)
                best_inventories = copy.deepcopy(inventories)
                best_prices = copy.deepcopy(prices)
                best_demand = copy.deepcopy(demand)
                best_obj = obj
                best_j = j
                if best_improve == 0:
                    break
            
            self.setups[j] = 1 - self.setups[j]
            neighbors_list.remove(j)
        
        if best_j != -1:
            self.update_current_solution(best_productions,best_inventories,best_prices,
                                         best_demand,best_j,-1,best_obj)
            return 1
        
        return 0
            
    def period_neighborhood_exploration(self,J,T,best_improve,setups_costs):
    
        neighbors_list = [t for t in range(T)]
        best_t = -1
        while len(neighbors_list) > 0:
            t = neighbors_list[0]
            self.setups[:,t] = 1 - self.setups[:,t]
            create_lingo_ltf_file(J,T,self.setups)
            os.system(f'runlingo nlp_model_J_{J}_T_{T}.ltf')
            productions,inventories,prices,demand,obj = self.solutions_reader_writer.read_setups_solution(J,T,setups_costs)
            if obj > self.obj:
                best_productions = copy.deepcopy(productions)
                best_inventories = copy.deepcopy(inventories)
                best_prices = copy.deepcopy(prices)
                best_demand = copy.deepcopy(demand)
                best_obj = obj
                best_t = t
                if best_improve == 0:
                    break
            
            self.setups[:,t] = 1 - self.setups[:,t]
            neighbors_list.remove(t)
        
        if best_t != -1:
            self.update_current_solution(best_productions,best_inventories,best_prices,
                                         best_demand,-1,best_t,best_obj)
            return 1
            
        return 0
        
    def update_current_solution(self,productions,inventories,prices,demand,j,t,obj):
    
        self.productions = copy.deepcopy(productions)
        self.inventories = copy.deepcopy(inventories)
        self.prices = copy.deepcopy(prices)
        self.demand = copy.deepcopy(demand)
        self.obj = obj

        if (j != -1) and (t != -1):
            self.setups[j][t] = 1 - self.setups[j][t]
        
        elif t == -1:
            self.setups[j] = 1 - self.setups[j]
        
        elif j == -1:
            self.setups[:,t] = 1 - self.setups[:,t]

        return


            
        