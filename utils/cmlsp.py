class Cmlsp:

    def __init__(self,J,T,c, h, a, v, prod_cap, lbs, 
                 c_dict, h_dict, a_dict, ubs, A, B,
                 seasonality_params):

        self.J = J
        self.T = T
        self.c = c
        self.h = h
        self.a = a
        self.v = v
        self.prod_cap = prod_cap
        self.lbs = lbs
        self.ubs = ubs
        self.c_dict = c_dict
        self.h_dict = h_dict
        self.a_dict = a_dict
        self.A = A
        self.B = B
        self.seasonality_params = seasonality_params

        return