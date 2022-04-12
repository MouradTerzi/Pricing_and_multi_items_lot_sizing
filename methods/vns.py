from solutions.solution_vns_setups import *

import time 
from utils.solutions_reader_writer import *

class Variable_neighborhood_search:

    def __init__(self):
        self.writer = Solutions_reader_writer()
        return 
    
    def variable_neighborhood_descent(self,instance,demand_form,
                                      results_file,solution_coding,
                                      so_init,best_improve):
        
        so = self.random_initialization(instance,demand_form,results_file,
                                        solution_coding,so_init)
        k = 1 
        while k <= 3:
            if k == 1:
                improve = so.product_period_neighborhood_exploration(instance.J,instance.T,
                                                                     best_improve,instance.a)
            elif k == 2:
                improve = so.product_neighborhood_exploration(instance.J,instance.T,
                                                              best_improve,instance.a)
            elif k == 3:
                improve = so.period_neighborhood_exploration(instance.J,instance.T,
                                                             best_improve,instance.a)
            if improve == 1:
                k = 1
            else:
                k += 1
        
        self.writer.save_solution(so,instance,results_file)

        return

    def random_initialization(self,instance,demand_form,results_file,
                              solution_coding,so_init):
        
        if solution_coding == 'prices':
            print('Not implemented class!')

        elif solution_coding == 'setups':
            so = Solution_vns_setups(instance.J,instance.T)
            so.generate_prices_lot_sizing_nlp_resolution(instance.J,instance.T,instance.a)
        
        return so

        