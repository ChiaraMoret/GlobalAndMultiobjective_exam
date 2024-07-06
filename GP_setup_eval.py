from GP_classes import *
from GP_evaluation import *

# this contains the laod_pickle function
from GP_seeds_pool import *


def pop_nl_switch(pop,pop_group,eval_group,variable_set,function_set,operators):
    '''
    computes the NL & balancedness of a given populations on a set of seeds different than those used in the evolution
    '''
    # pop_tts = {}
    switch_seeds(pop_group,eval_group)
    for tree in pop:
        tt = tree.truth_table(variable_set,function_set,operators)
        tree.NL = obj1(tt)
        # print(tt.values())
        # pop_tts[tuple(tt.values())] = tree.NL
        # pop_tts.append(tuple(tt.values()))
    # print(len(set(pop_tts)))
    switch_seeds(eval_group,pop_group)
    return  pop #, pop_tts


    
def experiment_switch_nl(file_name,eval_seeds_tts,function_set,operators, pop_type = 'both'):
    '''
    loads and computes the NL & balancedness of a given populations
    '''
    terminal_set, loaded_original_pop, loaded_pop = load_pickle(file_name)

    pop_seeds = [terminal for terminal in terminal_set if isinstance(terminal, Seed)]
    pop_seeds_tts = [seed.truth_table for seed in pop_seeds]
    all_seeds_tt = pop_seeds_tts + eval_seeds_tts
    pop_group,eval_group = create_groups(truth_tables = all_seeds_tt,seeds=pop_seeds)
    
    variable_set = term_to_var(terminal_set)
    match pop_type:
        case 'evo':
            pops = (loaded_pop,)
        case 'og':
            pops = (loaded_original_pop,)
        case 'both':
            pops = (loaded_original_pop,loaded_pop)
            
    for pop in pops:
        pop = pop_nl_switch(pop,pop_group,eval_group,variable_set,function_set,operators)
    return pops

def setup_nl_eval(experiments,n_vars,n_new_vars, n_seeds, function_set, operators, pop_type = 'both'):
    '''
    extracts all possible truth tables for a given setup
    a setup is characterized by the tuple (n_vars, n_new_vars, n_seeds)
    there may be more than one experiment runs for each setup
    '''
    if len(experiments)==0:
        return {}
    n_old_vars = n_vars - n_new_vars
    seeds_pool = generate_seeds_pool(n_old_vars, function_set, operators)
    seed_vars=tuple(f'ov{i+1}' for i in range(n_new_vars,n_vars))
    eval_seeds_tts = random.sample(seeds_pool,k=n_seeds)
    
    # we are intrested in the unique truth tables 
    # setup_tts = {}
    inital_setup_pop = []
    for experiment_file in experiments:
        
        # evaulate the non linearitiy for all truth tables produced by each single population
        experiment_pops = experiment_switch_nl(experiment_file,eval_seeds_tts,function_set,operators, pop_type = pop_type)
        inital_setup_pop.append(experiment_pops)
    regroup_setup_pop = list(zip(*inital_setup_pop))
    setup_pop = [sum(pop, []) for pop in regroup_setup_pop]
    return setup_pop#, setup_tts
     