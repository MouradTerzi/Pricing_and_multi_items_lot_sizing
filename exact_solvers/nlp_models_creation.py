import os
import itertools
import numpy as np 

def create_lingo_ltf_file(J,T,Y):
    
   instance_path = f'\'instances/products_{J}_periods_{T}.LDT'
   
   lingo_model = open(f'nlp_model_J_{J}_T_{T}.ltf','w')
   lingo_model.writelines('set default\nset echoin 1\n\n')

   write_general_data(lingo_model,instance_path)
   write_sets(lingo_model)
   write_logistics_data(lingo_model,instance_path)
   write_markets_data(lingo_model,instance_path)
   write_results_data(lingo_model,J,T)
   write_the_objective_function(lingo_model)
   write_logistics_constraints(lingo_model,J,T,Y)
   write_business_constraints(lingo_model)
   
   lingo_model.writelines(f'END\n\n')
   lingo_model.writelines(f'set terseo 1\n')
   lingo_model.writelines(f'go\n')
   lingo_model.writelines(f'nonz volume\n')
   lingo_model.writelines(f'quit\n')
   
   lingo_model.close()

   return 

def write_general_data(lingo_model,instance_path):

   lingo_model.writelines('MODEL:\nDATA:\n\n')
   lingo_model.writelines(f'PRODUCTS_NUMBER = @FILE({instance_path});\n')
   lingo_model.writelines(f'PERIODS_NUMBER = @FILE({instance_path});\n\n')
   lingo_model.writelines(f'ENDDATA\n\n')
   
   lingo_model.writelines(f'CALC:\n\n')
   lingo_model.writelines(f'@SET(\'TIMLIM\',30);\n')
   #lin_model.writelines(f'@SET(\'GLOBAL\',1);\n\n')
   #lingo_model.writelines(f'@SET(\'MULTIS\',4);\n')
   lingo_model.writelines(f'ENDCALC\n\n')

   return 

def write_sets(lingo_model):

   lingo_model.writelines(f'SETS:\n')

   lingo_model.writelines(f'PRODUCTS /1..PRODUCTS_NUMBER/;\n')
   lingo_model.writelines(f'PERIODS /1..PERIODS_NUMBER/;\n')
   
   lingo_model.writelines(f'OPERATIONAL_MARKET(PRODUCTS,PERIODS): C, H, SC, A, LB, UB, SEASONALITY, P, I, X;\n')

   lingo_model.writelines(f'CAPACITY_USED(PRODUCTS): V;\n')
   lingo_model.writelines(f'CAPACITY(PERIODS):PROD_CAP;\n')
   lingo_model.writelines(f'CROSS_PRICE(PRODUCTS,PRODUCTS):B;\n\n')

   lingo_model.writelines(f'ENDSETS\n\n')

def write_logistics_data(lingo_model,instance_path):
   
   lingo_model.writelines(f'DATA:\n\n')
   lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
   lingo_model.writelines('!------------------------------------------------------------- Logistic data --------------------------------------------------------------;\n')
   lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n')   
   
   lingo_model.writelines(f'C = @FILE({instance_path});\n')
   lingo_model.writelines(f'H = @FILE({instance_path});\n')
   lingo_model.writelines(f'SC = @FILE({instance_path});\n')
   lingo_model.writelines(f'V = @FILE({instance_path});\n')
   lingo_model.writelines(f'PROD_CAP = @FILE({instance_path});\n\n')
   
   return

def write_markets_data(lingo_model,instance_path):
       
   lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
   lingo_model.writelines('!------------------------------------------------------------- Market data --------------------------------------------------------------;\n')
   lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n')   
   
   lingo_model.writelines(f'LB = @FILE({instance_path});\n')
   lingo_model.writelines(f'UB = @FILE({instance_path});\n')
   lingo_model.writelines(f'A = @FILE({instance_path});\n')
   lingo_model.writelines(f'B = @FILE({instance_path});\n')
   lingo_model.writelines(f'SEASONALITY = @FILE({instance_path});')
   
   return 

def write_results_data(lingo_model,J,T):

   results_path = f'\'./results/J_{J}_T_{T}_setups_solution\''
  
   lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
   lingo_model.writelines('!------------------------------------------------------------- Results --------------------------------------------------------------;\n')
   lingo_model.writelines('!------------------------------------------------------------------------------------------------------------------------------------------;\n')   
   
   
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'Total profit of the horizon: \',@SUM(OPERATIONAL_MARKET(j,t): P(j,t)*SEASONALITY(j,t) \
   *A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))- C(j,t)*X(j,t) - H(j,t)*I(j,t)) ,@NEWLINE(1));\n')

   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'The resolution time is: \',@TIME(),\' seconds\',@NEWLINE(1));\n\n')
   
   """
      # Prouction and stock per (product - period)
   """
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'----------------------------------------------------------------------\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'  Product-period       Production                       Stock\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'----------------------------------------------------------------------\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITEFOR(OPERATIONAL_MARKET(j,t): 6*\' \',\'(\',j, \',\',t,\')\',6*\' \', X(j,t), 11*\' \', I(j,t),@NEWLINE(1));\n') 
   
   """
      # Prices per (product - period)
   """
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'  Product-period       Price\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITEFOR(OPERATIONAL_MARKET(j,t): 6*\' \',\'(\',j, \',\',t,\')\',6*\' \', P(j,t),@NEWLINE(1));\n') 
   """
      # Demand
   """
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'  Product-period       Generated demand\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITE(\'------------------------------------\',@NEWLINE(1));\n')
   lingo_model.writelines(f'@TEXT({results_path}) = @WRITEFOR(OPERATIONAL_MARKET(j,t): 6*\' \',\'(\',j, \',\',t,\')\',6*\' \',      SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1))) ,@NEWLINE(1));\n') 
   lingo_model.writelines(f'ENDDATA\n\n') 

   return 

def write_the_objective_function(lingo_model):

   lingo_model.writelines(f'!1: Objective function;\n')
   lingo_model.writelines(f'MAX = @SUM(OPERATIONAL_MARKET(j,t):P(j,t)*SEASONALITY(j,t)*A(j,t)*@PROD(CROSS_PRICE(j,i1):@POW(P(i1,t),B(j,i1)))- \
       C(j,t)*X(j,t) - H(j,t)*I(j,t));\n\n')
    
   return 

def write_logistics_constraints(lingo_model,J,T,Y):
       
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

   lingo_model.writelines(f'!6: Setup constraints;\n') 

   for j in range(J):
      for t in range(T):
            lingo_model.writelines(f'V({j+1})*X({j+1},{t+1}) - {Y[j][t]}*PROD_CAP({t+1}) <= 0;\n')            

   return 

def write_business_constraints(lingo_model):
       
   lingo_model.writelines(f'!------------------------------------------------------------------------------------------------------------------------------------------;\n') 
   lingo_model.writelines(f'!------------------------------------------------------------- Business cosntraints -------------------------------------------------------;\n')
   lingo_model.writelines(f'!------------------------------------------------------------------------------------------------------------------------------------------;\n\n')
   
   lingo_model.writelines(f'!7: Prices lower bounds constraints;\n') 
   lingo_model.writelines(f'@FOR(OPERATIONAL_MARKET(j,t): P(j,t) >= LB(j,t));\n') 

   lingo_model.writelines(f'!8: Prices upper bounds constraints;\n') 
   lingo_model.writelines(f'@FOR(OPERATIONAL_MARKET(j,t): P(j,t) <= UB(j,t));\n') 

   return 




