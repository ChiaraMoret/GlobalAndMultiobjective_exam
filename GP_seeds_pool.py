from GP_classes import *
from GP_evaluation import *
from GP_structure import *
import pickle
import glob

def all_truth_tables(n,bal=True):
    """
    Generate all possible truth tables with n variables.
    Only feasible for n<5
    """
    keys = tuple(product((0, 1), repeat=n))
    combinations = list(product([0, 1], repeat=2**n)) # Generate all possible truth tables
    
    truth_tables = []
    half = 2**(n-1)

    for combination in combinations:
        
        check_bal = True
        if bal:
            # if balancedeness is required, update check_bal so it's set to False when the thruth table is not balanced
            check_bal = (sum(combination) == half)

        if check_bal:
            # for us truth tables are dictionaries: create and store them 
            truth_table = {input:out for input,out in zip(keys,combination)}
            truth_tables.append(truth_table)
    
    return truth_tables


def max_nonlinearity_tts(n,bal=True):
    '''
    Returns a list of the truth tables with maximun non-linearity for n variables
    Only feasible for n<5
    '''
    # fist get all truth tables for n variables, then only keep the best ones
    truth_tables = all_truth_tables(n,bal)
    max_value = 0
    seeds_pool=[]
    for tt in truth_tables:
        NL = fast_nonlinearity(tt)
        # NL = obj_1(tt)
        if NL == max_value:
            seeds_pool.append(tt)
        elif NL > max_value:
            max_value = NL
            seeds_pool = [tt]
    print(f'for {n} variables max non-linearity for balanced functions is {max_value}')
    return seeds_pool



def load_pickle(file_name):
    '''
    loads a pickle file containg:
     - original pop
     - evolved pop
     - terminal set, meaning seeds and new variables
    '''
    with open(file_name, 'rb') as inp:
        loaded_original_pop, loaded_pop, terminal_set = pickle.load(inp)
    return terminal_set,loaded_original_pop,loaded_pop



def experiment_nl(file_name, function_set, operators, pop_type = 'evo'):
    '''
    This computes the 'obj1' value for each run, stored in a pickle file.
    obj1 is a good stand-in for non-linearity, as it accounts for balancedness
    Updates the non-linearity for all trees in the population, then returns the population
    as well as the truth tables in the population, with associated non-linearity
    '''
    terminal_set,loaded_original_pop,loaded_pop = load_pickle(file_name)
    variable_set = term_to_var(terminal_set)

    # take either the evolved or the original population, based on 'pop_type'
    pop = loaded_pop
    if pop_type == 'og':
        pop = loaded_original_pop

    pop_tts = {}
    for tree in pop:
        tt = tree.truth_table(variable_set,function_set,operators)
        # update population
        tree.NL = obj1(tt)
        # store the truth tables separately
        pop_tts[tuple(tt.values())] = tree.NL
    return pop,pop_tts



def truth_table(ground_truth):
    '''
    generates a truth table dictionary from a truth table array
    '''
    truth_table={}
    n_rows = len(ground_truth)
    n_variables = n_rows.bit_length() - 1
    i=0
    for input in product((0, 1), repeat=n_variables):
        truth_table[input] = ground_truth[i]
        i += 1
    return truth_table



def generate_seeds_pool(n_vars, function_set, operators):
    '''
    using all available experimens generate the best truth tables to be used as seeds
    '''
    # for less than 5 variables we comb through all possible seeds
    if n_vars < 5:
        print(f'for {n_vars} old variables comb through all possible seeds')
        candidates = max_nonlinearity_tts(n_vars)
        return candidates

    # for more than 5 variables we use all previous experiments
    print(f'for {n_vars} old variables use previuos results')
    # full_tts associates to each truth table from the experiments a NL
    full_tts = {}
    # each tuple (n_vars, n_new_vars, n_seeds) represents an experimental setup and is evaluated in one chuck
    for n_new_vars in range (1,n_vars):
        experiments = glob.glob(f'experiments/v{n_new_vars}_nv{n_vars}*')
        for file_name in experiments:
            _,pop_tts = experiment_nl(file_name,function_set,operators)
            full_tts.update(pop_tts)

    if full_tts:
        # Get the top 10% of the full population as possible seeds
        sorted_tts = sorted(full_tts, key=full_tts.get)
        n_candidates = int(len(sorted_tts)*0.10)
        top_candidates = sorted_tts[-n_candidates:]

        # Reconstruct the dictionaries for the truth tables
        candidates = [truth_table(truth) for truth in top_candidates]
        return candidates            
    else:
        raise ValueError(f'Found no experiments for {n_vars} total variables')
     