from solutions.solution_sa_prices import *
from solutions.solution_sa_setups import *

import time 
from utils.solutions_reader_writer import *

class Simulated_annealing:

    def __init__(self,T0,TF,cool):
        self.T0 = T0
        self.TF = TF
        self.cool = cool
        self.writer = Solutions_reader_writer()
        
        return 
    
    def simulated_annealing(self,instance,max_no_impr,demand_form,
                            results_file,solution_coding,so_init):
      
        no_impr,T0 = self.get_initial_variables()
        best_ch,so = self.random_initialization(instance,demand_form,results_file,
                                                solution_coding,so_init)
        
        start = time.time()
        while T0 >= self.TF and no_impr <= max_no_impr:
            s1 = copy.deepcopy(so)
            neighbor = self.generate_neighbors_solution(s1,instance,
                                                        demand_form,
                                                        solution_coding)

            best_ch,so,no_impr = self.update_current_solution(instance,so,s1,
                                                              best_ch,no_impr,
                                                              T0,results_file)
            T0 = self.cool*T0
            self.iteration += 1
            self.adjust_neighbors_operators_probabilities(solution_coding,no_impr,neighbor)
            
        return best_ch, time.time() - start 

    def get_initial_variables(self):
        
        no_impr = 0
        T0 = self.T0
        self.wn1 = 0.34
        self.wn2 = 0.33
        self.wn3 = 0.33
        self.iteration = 1
        self.neighbors_setup = np.zeros(3)
        self.neighbors_setup_improve = np.zeros(3)
        self.last_product_period_move_list = list()
        self.last_product_move_list = list()
        self.last_period_move_list = list()

        return no_impr,T0

    def random_initialization(self,instance,demand_form,results_file,
                              solution_coding,so_init):
        
        if solution_coding == 'prices':
            so = Solution_sa_prices(instance.J,instance.T)
            if so_init == 'gurobi':
                so.generate_random_solution_cmlsp_resolution(instance,demand_form)

            else:
                print('Not implemented method!')

        elif solution_coding == 'setups':
            so = Solution_sa_setups(instance.J,instance.T)
            so.generate_prices_lot_sizing_nlp_resolution(instance.J,instance.T,instance.a)
        
        best_ch = copy.deepcopy(so)
        self.writer.save_solution(best_ch,instance,results_file)
        
        return so,best_ch
    
    def generate_neighbors_solution(self,current_solution,instance,
                                    demand_form,solution_coding):
        
        if solution_coding == 'prices':
            current_solution.generate_neighbors_solution(instance,demand_form,self.wn1)
        
        elif solution_coding == 'setups':
            current_solution.generate_neighbors_solution(instance.J,instance.T,instance.a,
                                                         self.wn1,self.wn2,self.wn3,
                                                         self.last_product_period_move_list,
                                                         self.last_product_move_list,
                                                         self.last_period_move_list)
        
        return 

    def update_current_solution(self,instance,so,s1,best_ch,
                                no_impr,T0,results_file):
        
        if  s1.obj > so.obj:
            so = copy.deepcopy(s1)
            no_impr = 0
            if so.obj > best_ch.obj:
                best_ch = copy.deepcopy(so)
                self.writer.save_solution(best_ch,instance,results_file)
            
        else:
            r = random.uniform(0,1)
            if np.exp((s1.obj - so.obj)/T0) >= r:
                no_impr = 0
                so = copy.deepcopy(s1)
                   
            else:
                no_impr += 1
    
        return best_ch,so,no_impr

    def adjust_neighbors_operators_probabilities(self,solution_coding,no_impr,neighbor):
        
        if solution_coding == 'setups':
           self.adjust_neighbors_operators_probabilities_setups(no_impr,neighbor)
        
        elif solution_coding == 'prices':
            print('Not implemented method')
        
        return 
        
    def adjust_neighbors_operators_probabilities_setups(self,no_impr,neighbor):
        
        self.neighbors_setup[neighbor] += 1 #[n_ns1,n_ns2,n_ns3]
        if no_impr == 0:
            self.neighbors_setup_improve[neighbor] += 1 

        if self.iteration % 20 == 0:
            indexes = np.where(self.neighbors_setup_improve == 0)[0]
            if len(indexes) == 3: #No improvement after the application of the neighbors operators
                self.wn1 = 0.34
                self.wn2 = 0.33
                self.wn3 = 0.33
            
            else: #At least one improvement is occured after the application of the neighbors operators
                sc = np.zeros(3)
                for i in range(3):
                    if self.neighbors_setup[i] != 0:
                        sc[i] = self.neighbors_setup_improve[i]/self.neighbors_setup[i]

                self.wn1 = sc[0]/np.sum(sc)
                self.wn2 = sc[1]/np.sum(sc)
                self.wn3 = sc[2]/np.sum(sc)
                self.neighbors_setup_improve = np.zeros(3)  
            
            self.neighbors_setup = np.zeros(3)
    
        return 
