from solutions.solution import *
from solutions.solution_sa_prices import *
from solutions.solution_sa_setups import *
from solutions.solution_vns_setups import *

from utils.reader import *
from methods.sa import *
from methods.vns import *

if __name__ == '__main__':
    
    J,T = 5,6
    print('here!')
    instance = read_instance(J,T)
    vns = Variable_neighborhood_search()
    
    results_path = f'results/J_{J}_T_{T}_results'
    results_file = open(results_path,'w')
    vns.variable_neighborhood_descent(instance,'ISO-ELASTIC',
                                 results_file,'setups',
                                 'setups',1)
    
    
    #sa = Simulated_annealing(50,1,0.96)
    #results_path = f'results/J_{J}_T_{T}_results'
    #results_file = open(results_path,'w')
    #sa.simulated_annealing(instance,10,'ISO-ELASTIC',results_file,'setups','setups')
    #vns_sol = Solution_vns_setups(J,T)
    #vns_sol.generate_prices_lot_sizing_nlp_resolution(J,T,instance.a)
    #improve = vns_sol.product_period_neighborhood_exploration(J,T,1,instance.a)
    #improve = vns_sol.product_neighborhood_exploration(J,T,1,instance.a)
    #improve = vns_sol.period_neighborhood_exploration(J,T,1,instance.a)
    #print(improve)

    