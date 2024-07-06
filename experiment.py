from GP_classes import *
from GP_operators import *
from GP_evaluation import *
from GP_structure import *
from GP_seeds_pool import *
import argparse
import pickle
import os
from datetime import datetime




def str_to_func(func_name):
    evals = [fit1,fit2,fit3,obj1,obj2]
    evals_names = {eval.__name__: eval for eval in evals}
    if func_name in evals_names.keys():
        return evals_names[func_name]
    else:
        raise argparse.ArgumentTypeError(f"Function '{func_name}' is not supported.")

# PARSE ARGUMENTS ------------------------------------------------------
parser = argparse.ArgumentParser()

 
parser.add_argument('--pop_size', type=int) 
parser.add_argument('--max_depth', type=int)
parser.add_argument('--n_new_vars', type=int)
parser.add_argument('--n_old_vars', type=int)
parser.add_argument('--n_seeds', type=int) 
parser.add_argument('--n_groups', type=int) 
parser.add_argument('--obj', type=str_to_func)
parser.add_argument('--fit', type=str_to_func)
parser.add_argument('--max_evals', type=int)


args = parser.parse_args()

# operators and their arities are not changed
operators = {'AND' : operator.and_,
            'AND2' : CustomOperator.and2_,
            'OR' : operator.or_,
            'XOR' : operator.xor,
            'XNOR' : CustomOperator.xnor_,
            'NOT' : operator.not_,
            'IF' : CustomOperator.if_}
operator_arities = {
    'AND': 2,
    'AND2': 2,
    'OR': 2,
    'XOR': 2,
    'XNOR': 2,
    'IF': 3,
    'NOT': 1
}

function_set = list(operators.keys())

#population parameters
pop_size = args.pop_size
max_depth = args.max_depth

#new variables
n_new_vars = args.n_new_vars

#seeds parameter
n_old_vars = args.n_old_vars
seed_vars=tuple(f'ov{i+1}' for i in range(n_new_vars,n_old_vars+n_new_vars))
n_seeds = args.n_seeds
n_groups = args.n_groups
seeds_pool = generate_seeds_pool(n_old_vars, function_set, operators)



#eval parameters
obj = args.obj
fit = args.fit
print(f'obj is {obj.__name__}, fit is {fit.__name__}')
max_evals = args.max_evals
terminal_set,original_pop,pop = boolean_GA(function_set,operators,operator_arities,pop_size,max_depth,seed_vars,
                                           seeds_pool,n_seeds,n_groups,n_new_vars,obj,fit,max_evals)

# the final and original populatons are saved in a pickle file
current_datetime = datetime.now() # use to differentiate multiple runs of the same experiment
save_folder = 'experiments'
os.makedirs(save_folder, exist_ok=True)
save_file = f'{save_folder}/v{n_new_vars}_nv{n_new_vars+n_old_vars}_ns{n_seeds}_{fit.__name__}_{obj.__name__}_{max_evals}_{current_datetime.strftime("%Y_%m_%d_%H")}.pkl'


with open(save_file, 'wb') as outp:
    pickle.dump((original_pop, pop, terminal_set), outp, protocol=pickle.HIGHEST_PROTOCOL)
    # pickle.dump(original_pop, outp, protocol=pickle.HIGHEST_PROTOCOL)
    # pickle.dump(pop, outp, protocol=pickle.HIGHEST_PROTOCOL)
    # pickle.dump(terminal_set, outp, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Run saved to {save_file}')
