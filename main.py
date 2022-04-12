from solutions.solution import *
from solutions.solution_sa_prices import *
from solutions.solution_sa_setups import *
from utils.reader import *
from methods.sa import *

if __name__ == '__main__':
    
    J,T = 5,6
    instance = read_instance(J,T)
    sa = Simulated_annealing(50,1,0.96)
    
    results_path = f'results/J_{J}_T_{T}_results'
    results_file = open(results_path,'w')
    sa.resolution(instance,10,'ISO-ELASTIC',results_file,'setups','setups')
    