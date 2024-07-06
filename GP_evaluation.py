from GP_classes import *


#################################### OBJECTIVES #######################################

#note that these fns all take the truth table, not the tree, as input
def balancedness_penalty(truth_table):
    '''
    Computes how many bits have to be switched to reach balancedness
    '''
    # compute the balancedness penalty for a truth table
    ones = sum(truth_table.values())
    return int(abs(ones - len(truth_table)/2))

def delta_BAL(BAL):
    return int(BAL == 0)


def fwht(truth_table):
    """
    This algorithm allows for computation of the Fast Walsh–Hadamard Transform of a given thruth table
    Complexity nlogn
    """
    #this is the array where the WH transform will be stored 
    host_arr = list(truth_table.values())
    h = 1
    while h < len(host_arr):
        for i in range(0, len(host_arr), h * 2):
            for j in range(i, i + h):
                x = host_arr[j]
                y = host_arr[j + h]
                host_arr[j] = x + y
                host_arr[j + h] = x - y
        h *= 2
    return host_arr

def fast_spectrum(truth_table):
    '''
    Computes the Fast Walsh–Hadamard spectrum using the fast implementation of the Walsh–Hadamard Transform algorithm.
    The first value is just the balancess penality, therefore this is NOT accurate
    '''
    walsh_transform = fwht(truth_table) 
    # the fist element is weight(f), so remove it
    spec = [abs(v) for v in walsh_transform[1:]]    
    return spec

def fast_nonlinearity(truth_table):
    """
    Computes the non-linearity of a given truth table using the fast implementation of the Walsh-transform
    """
    max_spec = max(fast_spectrum(truth_table))
    return int((len(truth_table)/2) - max_spec)

def _dot_product(u,v): 
    '''
    mod2 dot product
    '''
    prod = np.dot(u,v)
    return prod%2
    
def WH_transform(truth_table):
    '''
    Naive implementation of the Walsh–Hadamard Transform of a given truth table
    '''
    vecs = truth_table.keys()
    compute_WH = lambda a: sum([(-1)**(truth_table[vec] ^ _dot_product(vec,a)) for vec in vecs])
    return [compute_WH(vec) for vec in vecs]

def WH_spectrum(truth_table):
    '''
    Computes the Fast Walsh–Hadamard spectrum using the naive implementation of the Walsh–Hadamard Transform algorithm.
    It is necessary as the first element is not the weight of the function
    '''
    walsh_transform = WH_transform(truth_table)
    spec = [abs(v) for v in walsh_transform]
    return spec


def obj1(truth_table):
    """
    The first objective considers balancedeness first,
    and non linearity once the function is perfectly balanced
    """
    BAL = balancedness_penalty(truth_table)
    if BAL != 0:
        return -BAL
    return fast_nonlinearity(truth_table)


def indicator(truth_table):
    """
    Normalized number of occurences of max non-lineary in WH spectrum
    """
    spec = WH_spectrum(truth_table)
    max_vals = spec.count(max(spec))
    return 1 - max_vals/len(truth_table)

def obj2(truth_table):
    """
    The second objective extends the first one 
    to consider the whole Walsh-Hadamard spectrum
    """
    BAL = balancedness_penalty(truth_table)
    if BAL != 0:
        return -BAL
    return fast_nonlinearity(truth_table) + indicator(truth_table)

############################################ FITNESSES ##########################################

def switch_seeds(group1:dict,group2:dict):
    '''
    changes the seeds from those in group1 to those in gruoup2
    '''
    for seed in group1.keys():
        assert len(seed.variables)==len(next(iter(group2[seed]))), f'You tried switching two seeds with different sets of variables'
        seed.truth_table = group2[seed]
        
def evaluate_all_groups(tree,obj,groups,variable_set,function_set,operators):
    '''
    Evaluates the truth table for a given tree for all groups of seeds provided as input.
    The groups of seeds are dictionaries, and the evaluation is performed according to the input objective function 'obj'
    '''
    evals=[]
    
    for i in range(len(groups)):
        # evaluate the construction with the current group
        eval_i=obj(tree.truth_table(variable_set,function_set,operators))
        evals.append(eval_i)
        # change the seeds from current one to the ones in the next group
        switch_seeds(groups[i],groups[(i+1) % len(groups)])
    return evals


def delta_maxval(val,maxval):
    """
    checks if val==maxval
    added the case maxval>val to handle obj1 since we are adding indicator(>0) to NL 
    """
    return int(val<=maxval)

def fit1(tree,obj,groups,variable_set,function_set,operators,max_NL):
    """
    most weigth given to the eval of group1
    """
    evals = evaluate_all_groups(tree,obj,groups,variable_set,function_set,operators)
    return evals[0] + delta_maxval(evals[0],max_NL) * sum(evals[1:])


def fit2(tree,obj,groups,variable_set,function_set,operators,max_NL):
    """ 
    'sum of all groups' approach 
    """
    evals = evaluate_all_groups(tree,obj,groups,variable_set,function_set,operators)
    return sum(evals)


def fit3(tree,obj,groups,variable_set,function_set,operators,max_NL):
    """ 
    minimum objective value among all seed groups (which is maximized as a consequence)
    """
    evals = evaluate_all_groups(tree,obj,groups,variable_set,function_set,operators)
    return min(evals)    


                 ############ PENALITY ########
def penalty_step(tree,fitness,terminal_set):
    """ 
    penalizes a construction if it does not include all the input terminals
    the fitness must be calculated before the step
    """
    leaves = {leaf.name for leaf in PreOrderIter(tree) if not leaf.children}
    missing_terminals = set(terminal_set)-leaves
    return fitness/(1+len(missing_terminals))