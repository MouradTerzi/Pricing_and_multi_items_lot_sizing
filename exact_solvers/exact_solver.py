import gurobipy as gp
from gurobipy import *
import numpy as np 
import os

class EXACT_SOLVER:

    def __init__(self):
        return 
    
    def cmlsp_resolution(self,J,T,demand,c,h,a,v,prod_cap):
    
        """
           # Get indexes
        """
        j_t_indexes = {(j+1,t+1) for j in range(J) for t in range(T)}

        """
            # Create the gurobi model 
        """

        model = gp.Model('cmlsp')
        X = model.addVars(j_t_indexes, vtype = GRB.CONTINUOUS, name ="X")
        I = model.addVars(j_t_indexes, vtype = GRB.CONTINUOUS, name ="I")
        Y = model.addVars(j_t_indexes, vtype = GRB.BINARY, name ="Y")
    
        """
            # Add the objective function
        """

        obj_list = list()

        for t in range(T): 
            for j in range(J):
                costs_j_t = (c[(j+1,t+1)]*X[(j+1,t+1)] + h[(j+1,t+1)]*I[(j+1,t+1)] + a[(j+1,t+1)]*Y[(j+1,t+1)])
                obj_list.append(costs_j_t)
            
        obj = gp.quicksum(obj_list)
        model.setObjective(obj,GRB.MINIMIZE)
        model.Params.LogToConsole = 0

        """  
           Add production capacity constraints
        """
        model.addConstrs((gp.quicksum(v[j]*X[j+1,t+1] for j in range(J)) <= prod_cap[t] for t in range(T)), name ="prod_cap")

        """ 
           # Inventory for t = 1 
        """
        model.addConstrs((X[(j+1,1)] - demand[j][0] == I[(j+1,1)] for j in range(J)),name = "inventory_1")
        
        """ 
           # Inventory for 2 <= t <= T - 1 
        """
        model.addConstrs((X[(j+1,t)] + I[(j+1,t-1)] - demand[j][t-1] == I[(j+1,t)] for j in range(J) for t in range(2,T)) ,name = "inventory")
    
        """ 
           # Inventory for t = T
        """
        model.addConstrs((X[(j+1,T)] + I[(j+1,T-1)]- demand[j][T-1] == 0 for j in range(J)),name = "inventory_T")
        
        """
           # Setup constraints 
        """ 
        model.addConstrs((v[j]*X[(j+1,t+1)] <= Y[(j+1,t+1)]*prod_cap[t] for j in range(J) for t in range(T)),name = "setup")
        
        try:
            model.optimize()
            setups,productions,inventories = self.construct_lot_sizing_array_variable(J,T,X,I,Y)

        except AttributeError:
            print('Model is infeasible!')
            return np.ones((J,T)),np.ones((J,T)),np.ones((J,T)),-1

        return setups,productions,inventories, model.objVal

    def clp_resolution(self,J,T,demand,c,h,a,v,prod_cap,Y):
    
        """
           # Get indexes
        """
        j_t_indexes = {(j+1,t+1) for j in range(J) for t in range(T)}

        """
            # Create the gurobi model 
        """

        model = gp.Model('cmlsp')
        X = model.addVars(j_t_indexes, vtype = GRB.CONTINUOUS, name ="X")
        I = model.addVars(j_t_indexes, vtype = GRB.CONTINUOUS, name ="I")

        """
            # Add the objective function
        """

        obj_list = list()

        for t in range(T): 
            for j in range(J):
                costs_j_t = (c[(j+1,t+1)]*X[(j+1,t+1)] + h[(j+1,t+1)]*I[(j+1,t+1)])
                obj_list.append(costs_j_t)
            
        obj = gp.quicksum(obj_list)
        model.setObjective(obj,GRB.MINIMIZE)
        model.Params.LogToConsole = 0

        """  
           Add production capacity constraints
        """
        model.addConstrs((gp.quicksum(v[j]*X[j+1,t+1] for j in range(J)) <= prod_cap[t] for t in range(T)), name ="prod_cap")

        """ 
           # Inventory for t = 1 
        """
        model.addConstrs((X[(j+1,1)] - demand[j][0] == I[(j+1,1)] for j in range(J)),name = "inventory_1")
        
        """ 
           # Inventory for 2 <= t <= T - 1 
        """
        model.addConstrs((X[(j+1,t)] + I[(j+1,t-1)] - demand[j][t-1] == I[(j+1,t)] for j in range(J) for t in range(2,T)) ,name = "inventory")
    
        """ 
           # Inventory for t = T
        """
        model.addConstrs((X[(j+1,T)] + I[(j+1,T-1)]- demand[j][T-1] == 0 for j in range(J)),name = "inventory_T")
        
        """
           # Setup constraints 
        """ 
        model.addConstrs((X[(j,t)] == 0 for j,t in j_t_indexes if Y[j-1][t-1] == 0))
        try:
            model.optimize()
            productions,inventories = self.construct_X_I_arrays(J,T,X,I)
            
        except AttributeError:
            #print('Model is infeasible!')
            return np.ones((J,T)),np.ones((J,T)),-1
        
        return productions,inventories, model.objVal

    def construct_lot_sizing_array_variable(self,J,T,X,I,Y):
        
        setups = np.zeros((J,T))
        productions = np.zeros((J,T))
        inventories = np.zeros((J,T))

        for j in range(J):
            for t in range(T):
                setups[j][t] = Y[j+1,t+1].x
                productions[j][t] = X[j+1,t+1].x
                inventories[j][t] = I[j+1,t+1].x
        
        return setups,productions,inventories
    
    def construct_X_I_arrays(self,J,T,X,I):
        
        productions = np.zeros((J,T))
        inventories = np.zeros((J,T))

        for j in range(J):
            for t in range(T):
                productions[j][t] = X[j+1,t+1].x
                inventories[j][t] = I[j+1,t+1].x
        
        return productions,inventories

    def nlp_resolution(self,J,T,instance_size,demand,seasonality,
                       relation,diag_dom,instance_number,Y):
        
        self.create_lingo_ltf_file(J,T,instance_size,demand,seasonality,
                                   relation,diag_dom,instance_number,Y)
        
        os.system(f'runlingo initial_model_J_{J}_T_{T}_{relation}_{diag_dom}_{instance_number}.ltf')

    def create_lingo_ltf_file(self,J,T,instance_size,demand,seasonality,
                              relation,diag_dom,instance_number,Y):
        
        instance_folder_path = f'\'../Instances/{instance_size}/{demand}/SC{seasonality}/{relation}_products/'
        instance = f'Instance_{instance_number}_J_{J}_T_{T}_{relation}_{diag_dom}.LDT\''
   
        lin_model = open(f'initial_model_J_{J}_T_{T}_{relation}_{diag_dom}_{instance_number}.ltf','w')
        lin_model.writelines('set default\nset echoin 1\n\n')

        """
        # First data section
        """
        lin_model.writelines('MODEL:\nDATA:\n\n')
        lin_model.writelines(f'!Initialization of the general data {instance};\n')
        lin_model.writelines(f'PRODUCTS_NUMBER = @FILE({instance_folder_path}{instance});\n')
        lin_model.writelines(f'PERIODS_NUMBER = @FILE({instance_folder_path}{instance});\n\n')
        lin_model.writelines(f'ENDDATA\n\n')
    
        lin_model.writelines(f'CALC:\n\n')
        lin_model.writelines(f'@SET(\'TIMLIM\',200);\n')
        lin_model.writelines(f'@SET(\'MXMEMB \',128);\n')
        lin_model.writelines(f'ENDCALC\n\n')

        """
        # Sets section
        """
        self.write_sets(instance_folder_path,instance,lin_model)

        """
            # Data section 
        """
        lin_model.writelines(f'DATA:\n\n')
        self.write_logistics_data(instance_folder_path, instance, lin_model)
        self.write_markets_data(instance_folder_path, instance, lin_model)
        self.write_results_data(lin_model)

        lin_model.writelines(f'ENDDATA\n\n')

        """
        # Objective function 
        """
        self.write_the_objective_function(lin_model)

        """
        # Logistics constraints 
        """
        self.write_logistics_constraints(lin_model,Y)

        """
        # Business constraints
        """
        self.write_business_constraints(lin_model)

        return 

    def write_sets(self,instance_folder_path, instance, lingo_model):

        lingo_model.writelines(f'SETS:\n')

        lingo_model.writelines(f'PRODUCTS /1..PRODUCTS_NUMBER/;\n')
        lingo_model.writelines(f'PERIODS /1..PERIODS_NUMBER/;\n')
        lingo_model.writelines(f'OPERATIONAL_MARKET(PRODUCTS,PERIODS): C, H, SC, A, LB, UB, SEASONALITY, P, I, X;\n')
        lingo_model.writelines(f'CAPACITY_USED(PRODUCTS): V;\n')
        lingo_model.writelines(f'CAPACITY(PERIODS):PROD_CAP;\n')
        lingo_model.writelines(f'CROSS_PRICE(PRODUCTS,PRODUCTS):B;\n\n')

        lingo_model.writelines(f'ENDSETS\n\n')

        return 

    def write_logistics_data(self,instance_folder_path, instance, lingo_model):
    
        lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
        lingo_model.writelines('!------------------------------------------------------------- Logistic data --------------------------------------------------------------;\n')
        lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n')   
        
        lingo_model.writelines(f'C = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'H = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'SC = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'V = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'PROD_CAP = @FILE({instance_folder_path}{instance});\n\n')
    
        return
    
    def write_markets_data(self,instance_folder_path, instance, lingo_model):
       
        lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
        lingo_model.writelines('!------------------------------------------------------------- Market data --------------------------------------------------------------;\n')
        lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n')   
        
        lingo_model.writelines(f'LB = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'UB = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'A = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'B = @FILE({instance_folder_path}{instance});\n')
        lingo_model.writelines(f'SEASONALITY = @FILE({instance_folder_path}{instance});')
        
        return 

    def write_results_data(self,lingo_model):

        results_folder_path = 'initial'
        results = '_solution'
        
        lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
        lingo_model.writelines('!------------------------------------------------------------- Results --------------------------------------------------------------;\n')
        lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n')   

        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'Total profit of the horizon: \',@SUM(OPERATIONAL_MARKET(j,t): P(j,t)*SEASONALITY(j,t) \
        *A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))- C(j,t)*X(j,t) - H(j,t)*I(j,t)) ,@NEWLINE(1));\n')
        
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'The resolution time is: \',@TIME(),\' seconds\',@NEWLINE(1));\n\n')
        
        """
            # Prouction and stock per (product - period)
        """

        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'----------------------------------------------------------------------\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'  Product-period       Production                       Stock\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'----------------------------------------------------------------------\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITEFOR(OPERATIONAL_MARKET(j,t): 6*\' \',\'(\',j, \',\',t,\')\',6*\' \', X(j,t), 11*\' \', I(j,t),@NEWLINE(1));\n') 
        
        """
            # Prices per (product - period)
        """
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'  Product-period       Price\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITEFOR(OPERATIONAL_MARKET(j,t): 6*\' \',\'(\',j, \',\',t,\')\',6*\' \', P(j,t),@NEWLINE(1));\n') 
        """
            # Demand
        """
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'  Product-period       Generated demand\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
        lingo_model.writelines(f'@TEXT({results_folder_path}{results}) = @WRITEFOR(OPERATIONAL_MARKET(j,t): 6*\' \',\'(\',j, \',\',t,\')\',6*\' \',      SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1))) ,@NEWLINE(1));\n') 
        
        return 

    def write_the_objective_function(self,lingo_model):

        lingo_model.writelines(f'!1: Objective function;\n')
        lingo_model.writelines(f'MAX = @SUM(OPERATIONAL_MARKET(j,t):P(j,t)*SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))- \
            C(j,t)*X(j,t) - H(j,t)*I(j,t));\n\n')
            
        return 

    def write_logistics_constraints(self,lingo_model,Y):
        
        lingo_model.writelines(f'!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
        lingo_model.writelines(f'!------------------------------------------------------------- Logistic constraints -------------------------------------------------------;\n')
        lingo_model.writelines(f'!------------------------------------------------------------------------------------------------------------------------------------------;\n\n')
                                        
        lingo_model.writelines(f'!2: Capacity constraints;\n') 
        lingo_model.writelines(f'@FOR(PERIODS(t): @SUM(CAPACITY_USED(j): V(j)*X(j,t)) <= PROD_CAP(t));\n\n') 
        
        lingo_model.writelines(f'!3: Inventory constraints for t = 1;\n') 
        lingo_model.writelines(f'@FOR(OPERATIONAL_MARKET(j,t) | t#EQ# 1: X(j,t) - \
        (SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))) = I(j,t));\n\n')

        lingo_model.writelines(f'!4: Inventory constraints for t = 2, ..., PERIODS_NUMBER -  1;\n\n') 
        lingo_model.writelines(f'@FOR(OPERATIONAL_MARKET(j,t) | t#GE# 2 #AND# t #LE# PERIODS_NUMBER - 1: X(j,t) +I(j,t-1) - \
        (SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))) = I(j,t));\n')
        
        lingo_model.writelines(f'!5: Inventory constraints for t = T;\n') 
        lingo_model.writelines('@FOR(OPERATIONAL_MARKET(j,t) | t#EQ# PERIODS_NUMBER #AND# t #NE# 1: X(j,t) + I(j,t-1) - (SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))) = 0);\n\n')
        indexes = np.where(Y == 0)
        for j,t in zip(indexes[0],indexes[1]):
            lingo_model.writelines(f'X({j+1},{t+1}) = 0;\n')

        return 

    def write_business_constraints(self,lingo_model):
        
        lingo_model.writelines(f'!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
        lingo_model.writelines(f'!------------------------------------------------------------- Business cosntraints -------------------------------------------------------;\n')
        lingo_model.writelines(f'!------------------------------------------------------------------------------------------------------------------------------------------;\n\n')
        
        lingo_model.writelines(f'!7: Prices lower bounds constraints;\n') 
        lingo_model.writelines(f'@FOR(OPERATIONAL_MARKET(j,t): P(j,t) >= LB(j,t));\n') 

        lingo_model.writelines(f'!8: Prices upper bounds constraints;\n') 
        lingo_model.writelines(f'@FOR(OPERATIONAL_MARKET(j,t): P(j,t) <= UB(j,t));\n') 

        return 

