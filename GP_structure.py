#from itertools import product
from GP_classes import *
from GP_evaluation import *
from GP_operators import *
import random
from tqdm import tqdm




def term_to_var(terminal_set):
    '''
    The terminal set contains the new variables and the seeds
    This function outputs an oredered set of variables, which includes the new variables' names 
    and the names of the varaibles of the seeds
    '''
    candidates = []
    for terminal in terminal_set:
        
        # add new variables directly
        if isinstance(terminal, str): 
            candidates.append(terminal)
            
        # add variables inherited from seeds
        elif isinstance(terminal, Seed): 
            var_to_add=[var for var in terminal.variables if var not in candidates] # keep the order, avoid duplicates
            candidates+=var_to_add
            
    return candidates


def init_population(pop_size, max_depth,function_set,terminal_set,operator_arities,p_op,p_ter):
  """ 
  Creates a population of size 'pop_size'.
  Each tree in the population can have depth up to max_depth
  """
  pop = [create_random_tree(max_depth,function_set,terminal_set,operator_arities,p_op,p_ter) for _ in range(0, pop_size)]
  return pop

def update_fitnesses(pop,obj,fit,groups,terminal_set,variable_set,function_set,operators,penalty=True,NL=None):
  """ 
  Updates the 'fitness' property of all trees in the population
  """
  for tree in pop:
    fitness = fit(tree, obj, groups, variable_set,function_set,operators,NL)
    if penalty:
      fitness = penalty_step(tree,fitness,terminal_set)
    tree.fitness = fitness


#################

def boolean_GA(function_set,operators,operator_arities,pop_size,max_depth,seed_vars,seeds_pool,n_seeds,n_groups,n_new_vars,obj,fit,max_evals):
    '''
    Full GA for evolving constructions
    Return both the original population and its evolution.
    Note that quite a few inputs must be provided, including the function set, the operators, 
    the pool of seeds from which to pick from, and the names of the variables for those seeds
    '''

    # create n_groups groups of n_seeds seeds
    selected_seeds = random.sample(seeds_pool,k=n_seeds*n_groups)
    seeds = create_seeds(selected_seeds,n_seeds,seed_vars)
    groups = create_groups(truth_tables = selected_seeds,seeds=seeds)
    print(f'seeds are {[str(seed) for seed in seeds]}')

    # the terminal set and variable set are generated consistently with the required number of new variables
    terminal_set = list(seeds) + [f'v{i+1}' for i in range(n_new_vars)]
    variable_set = term_to_var(terminal_set)
    
    # best known linearities in cases n=4,...,16
    best_NL=[4,12,26,56,116,240,492,992,2012,4036,8120,16272,32638]
    NL=best_NL[len(variable_set)-4]

    # generate the population of trees
    # probability that a given node at depth <max_depth will be a leaf
    p_ter = 0.25
    # probability that a given node at depth <max_depth will be an operator
    p_op = 1 - p_ter
    pop = init_population(pop_size, max_depth,function_set,terminal_set,operator_arities,p_op,p_ter)

    # evaluate and store the orinal population
    update_fitnesses(pop,obj,fit,groups,terminal_set,variable_set,function_set,operators,NL=NL)
    original_pop = pop.copy()
    print(f'initialization done. Now evolve:')
    
    for n_eval in tqdm(range(max_evals)):
        
        # selection
        parent1, parent2 = three_turnament_selection(pop)

        # crossover, sampled uniformly between available crossover types
        crossover = random.choice([tree_crossover, uniform_crossover, one_point_crossover,context_preserving_crossover, size_fair_crossover])
        child1 = crossover(parent1, parent2,max_depth)
        
        # mutation, which happens with probability 0.5
        if random.random()<0.5:
            child1 = subtree_mutation(child1,function_set,terminal_set,operator_arities,p_op,p_ter,max_depth)
            
        pop.append(child1)

        assert len(pop) == pop_size, f'pop_size was {len(pop)} but was expecting {pop_size}' # checks that the population size is invariant

        # fitness eval
        child1.fitness = fit(child1,obj,groups,variable_set,function_set,operators,NL)
        child1.fitness = penalty_step(child1,child1.fitness,terminal_set)
        
    return terminal_set,original_pop,pop 





