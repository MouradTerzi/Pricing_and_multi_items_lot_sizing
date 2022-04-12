import numpy as np 

class Solutions_reader_writer:

    def save_solution(self,solution,instance,results_file):

        results_file.writelines('Production planning:\n')
        for j in range(instance.J):
            X_j = [str(round(solution.productions[j][t],2)) for t in range(instance.T)]
            results_file.writelines(' '.join(X_j)+'\n')
        results_file.writelines('\n\n')

        results_file.writelines('Prices:\n')
        for j in range(instance.J):
            P_j = [str(round(solution.prices[j][t],2)) for t in range(instance.T)]
            results_file.writelines(' '.join(P_j)+'\n')
        results_file.writelines('\n\n')

        results_file.writelines('Inventory:\n')
        for j in range(instance.J):
            I_j = [str(round(solution.inventories[j][t],2)) for t in range(instance.T)]
            results_file.writelines(' '.join(I_j)+'\n')
        results_file.writelines('\n\n')

        results_file.writelines(f'Total profit:{str(solution.obj)}\n')

        used_capacity = np.dot(instance.v,solution.productions)
        violated_capacity = np.where(used_capacity - instance.prod_cap > 0, 100*(used_capacity - instance.prod_cap)/instance.prod_cap, 0)
        violated_capacity = np.around(violated_capacity,decimals = 1)
        
        per_violated_capacity = [str(violated_capacity[t]) for t in range(instance.T)]
        results_file.writelines('Percentage of violated capacity:\n')
        results_file.writelines(' | '.join(per_violated_capacity)+'\n')
        results_file.writelines(f'======================================================================================================================\n')

        return 
    
    def read_setups_solution(self,J,T,setups_costs):
        
        results_path = f'results/J_{J}_T_{T}_setups_solution'
        
        productions = np.zeros((J,T))
        inventories = np.zeros((J,T))
        prices = np.zeros((J,T))
        demand = np.zeros((J,T))
    
        results = open(results_path,'r').read().split('\n')
        start = 5
        for j in range(J):
            for t in range(T):
                line = results[start + j*T + t].split(' ')
                line = [e for e in line if e!='']
                productions[j][t] = float(line[1])
                inventories[j][t] = float(line[2])
        
        start+= J*T + 3
        for j in range(J):
            for t in range(T):
                line = line = results[start + j*T + t].split(' ')
                line = [e for e in line if e!='']
                prices[j][t] = float(line[1])

        start += J*T + 3
        for j in range(J):
            for t in range(T):
                line = line = results[start + j*T + t].split(' ')
                line = [e for e in line if e!='']
                demand[j][t] = float(line[1])
        
        
        setups = np.where(productions>0,1,0)
        obj = float(results[0].split(':')[1])
        obj -= np.sum(np.multiply(setups,setups_costs))
        
        return productions,inventories,prices,demand,obj