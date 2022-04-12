import random 
import copy 
import time

from .solution import *
from exact_solvers.nlp_models_creation import *
from utils.solutions_reader_writer import *

class Solution_sa_setups(Solution):

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
    
    def generate_neighbors_solution(self,J,T,setups_costs,wn1,wn2,wn3,
                                    last_product_period_move_list,
                                    last_product_move_list,
                                    last_period_move_list):
        #1. Generate neighbors setups
        r = random.uniform(0,1)
        if r <= wn1:
            self.generate_neighbors_product_period(J,T,last_product_period_move_list)
            if len(last_product_period_move_list) > T:
                del last_product_period_move_list[0]
            neighbor = 0
        
        elif r <= (wn1 + wn2):
            self.generate_neighbors_product(J,T,last_product_move_list)
            if len(last_product_move_list) == J:
                del last_product_move_list[0]
            neighbor = 1
        
        else:
            self.generate_neighbors_period(J,T,last_period_move_list)
            if len(last_period_move_list) == T-1:
                del last_period_move_list[0]
            neighbor = 2
        
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
        
        return neighbor
    
    def generate_neighbors_product_period(self,J,T,last_product_period_move_list):
        
        #1. Consider only (j,t) for which X-D < 0
        indexes = np.where(self.productions - self.demand < 0)
        neighbors_list = [(j,t) for (j,t) in zip(indexes[0],indexes[1])]
    
        while len(neighbors_list) > 0:
            j,t = random.choice(neighbors_list)
            if (j,t) not in last_product_period_move_list:
               self.setups[j][t] = 1 - self.setups[j][t]
               last_product_period_move_list.append((j,t))
               return 
            
            else:
                neighbors_list.remove((j,t))
        
        #2. If no neighbors from 1, consider all the tuples (j,t)
        neighbors_list = [(j,t) for j in range(J) for t in range(T)] 
        j,t = random.choice(neighbors_list)
        while (j,t) in last_j_t_move_list:
            neighbors_list.remove((j,t))
            j,t = random.choice(neighbors_list) 

        self.setups[j][t] = 1 - self.setups[j][t]
        last_j_t_move_list.append((j,t))
        
        return 
    
    def generate_neighbors_product(self,J,T,last_product_move_list):

        neighbors_list = [j for j in range(J)]
        j = random.choice(neighbors_list)
        while j in last_product_move_list:
           neighbors_list.remove(j)
           j = random.choice(neighbors_list)
        
        last_product_move_list.append(j)
        self.setups[j] = 1 - self.setups[j]
        
        return

    def generate_neighbors_period(self,J,T,last_period_move_list):

        neighbors_list  = [t for t in range(1,T)]
        t = random.choice(neighbors_list)
        while t in last_period_move_list:
           neighbors_list.remove(t)
           t = random.choice(neighbors_list)
        
        last_period_move_list.append(t)
        self.setups[:,t] = 1 - self.setups[:,t]
        
        return  
    



