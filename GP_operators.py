from GP_classes import *
from copy import deepcopy


def three_turnament_selection(population):
    '''
    selects three indivisuals at random from the population
    and returns the top two
    '''
    tournament = random.sample(population, 3)
    maxes = [tree.fitness for tree in tournament]
    # sort the tournament by fitness (higher fitness is better)
    tournament.sort(key=lambda tree: tree.fitness)
    # remove the worst performer from the population
    population.remove(tournament[0])
    return tournament[1:]

################################## CROSSOVERS #################################################

def replace_subtree(tree, dangle, old_subtree, new_subtree):
    """
    Replace 'subtree1' in 'tree' with 'subtree2' from a donor
    'dangle' is the parent of old_subtree
    """ 
    subtree = deepcopy(new_subtree)
    # if the crossover point is the root just copy the subtree
    if dangle is None:
        tree = subtree
        tree.parent = None
        return tree
    # if the crossover point is not the root, the children list of the dangle point must be updated to include new_subtree
    new_children=()
    for i, child in enumerate(dangle.children):
        if child == old_subtree:
            subtree.parent = dangle
            new_children= new_children + (subtree,)
        else:
            new_children= new_children + (child,)

    dangle.children = new_children
    return tree


             ########## TREE CROSSOVER ##########

def select_subtree(node,residual_depth = None):
    '''
    Randomly select a subtree in the tree rooted at 'node'
    subtree can have depth up to than 'residual_depth'
    '''
    # if no residual_depth is providedd, all subtrees rooted at 'node' can be chosen
    if residual_depth is None:
        residual_depth = node.compute_depth()
        
    candidates = [child for child in PreOrderIter(node) if child.compute_depth()<=residual_depth]
    selected = random.choice(candidates)
    
    return selected, selected.parent



def tree_crossover(parent1, parent2, max_depth):
    '''
    Simple tree crossover: pick a random point in each tree and switch the subrtrees rooted in the selected nodes
    '''
    # Make copies of parent1 to avoid modifying it directly
    child1 = deepcopy(parent1)
    #reset the fitnesses for the copies
    child1.fitness = None

    crossover_node1,graft_point1 = select_subtree(child1)
    # the resulting child must have depth <= max_depth; this is the contraint on the second subtree that ensures this condition is met  
    residual_depth = max_depth - crossover_node1.depth
    crossover_node2, _ = select_subtree(parent2, residual_depth)
    
    child1= replace_subtree(child1,graft_point1, crossover_node1, crossover_node2)
    return child1



        ############ UNIFORM CROSSOVER ###########

def descent_common_region(tree1,tree2):
    """  
    Given two trees traverses common region on the root, performing any exchange
    The common region is the region were the two trees have overlapping graphs, starting from the root
    No condition is placed on the name of the nodes, only on their arity
    """
    # check that tree1 and tree2 have equal arity: you are in the common region
    if len(tree1.children) == len(tree2.children):
        # no iterations here if either nodes are a leaf (arity=0)
        if random.random() < 0.5:
            # with probability 0.5, exchange a single node at this level 
            tree1.name = tree2.name
        for child1, child2 in zip(tree1.children,tree2.children):
            child1 = descent_common_region(child1,child2)

    # you have reached an edge point on the common region
    else:    
        # with probability 0.5, perform a subtree exchange at this level 
        if random.random() < 0.5:
            tree1 = replace_subtree(tree1, tree1.parent, tree1, tree2)
    return tree1


def uniform_crossover(parent1, parent2, max_depth):
    '''
    Uniform crossver: traverse the tree; at any point in the common region two corresponding nodes may be switched;
    subtrees rooted at the edge of the common region may also be exchanged 
    '''
    # Make copies of the parents to avoid modifying them directly
    child1 = deepcopy(parent1)
    child1.fitness = None
    
    child1 = descent_common_region(child1,parent2)
    return child1


            ########### ONE-POINT CROSSOVER ############
def update_common_region(tree1,tree2,common_region):
    """  
    Given two trees returns the common region on the root
    The common region is the region were the two trees have overlapping graphs, starting from the root
    No condition is placed on the name of the nodes, only on their arity
    """
    # add the nodes to the common region
    common_region.append((tree1,tree2))
    
    # check that tree1 and tree2 have equal arity, and iterate
    if len(tree1.children) == len(tree2.children):
        # no iterations here if either nodes are a leaf (arity=0)
        for child1,child2 in zip(tree1.children,tree2.children):
            # recursive update
            update_common_region(child1,child2,common_region)


def one_point_crossover(parent1,parent2,max_depth):
    """ 
    one-point crossover: selects one crossover point uniformly from the common region of the two parents
    """
    child1 = deepcopy(parent1)
    child1.fitness = None

    # get the common region between the 2 parents
    common_region=[]
    update_common_region(child1,parent2,common_region)

    # select at random the crossover nodes and also store their parents
    crossover_node1,crossover_node2 = random.choice(common_region)
    graft_point1,graft_point2=(crossover_node1.parent,crossover_node2.parent)
    # grafting
    child1 = replace_subtree(child1,graft_point1, crossover_node1, crossover_node2)

    return child1


            ############# CONTEXT-PRESERVING CROSSOVER ##################
def update_common_coords(tree1,tree2,common_coords):
    """  
    Given two trees returns the common coordinates on the root
    The common coordinates is set of nodes which have the same coordinates in the two trees
    No condition is placed on the name of the nodes, only on their position
    """
    # add the nodes to the common region
    common_coords.append((tree1,tree2))

    # zipping guarantees that only children in the same positions are iterated over
    for child1,child2 in zip(tree1.children,tree2.children):
        update_common_coords(child1,child2,common_coords)

def context_preserving_crossover(parent1,parent2,max_depth):
    """ 
    Context-preserving crossover: the crossover points are constrained 
    to have the same coordinates, but are not limited to the common region
    """
    
    child1 = deepcopy(parent1)
    child1.fitness = None

    # get the common coordinates region between the 2 parents
    common_coords=[]
    update_common_coords(child1,parent2,common_coords)
    
    # select at random the crossover nodes and also store their parents
    crossover_node1,crossover_node2 = random.choice(common_coords)
    graft_point1,graft_point2=(crossover_node1.parent,crossover_node2.parent)
    
    # grafting
    child1 = replace_subtree(child1,graft_point1, crossover_node1, crossover_node2)

    return child1


        ####### SIZE-FAIR CROSSOVER #####
def sf_select_second_crossover(node,cut_subtree,residual_depth):
    """
    takes care of all the computations for selecting the right donor subtree from 'node'
    the subrtree must be size-fair with respect to 'cut_subtree', and must have depth <= 'residual_depth'
    """
    
    cut_size = cut_subtree.size()
    # donor subreee must not be too big w.r.t cut subtree
    max_subtree_size = 1+2*cut_size

    # Filter nodes whose size exceeds `max_subtree_size`
    all_sizes = {child: size for child in PreOrderIter(node) if (size := child.size()) < max_subtree_size and child.compute_depth () <= residual_depth}    
    
    # populate n_plus,n_minus,n_0: subtrees that are respectively longer, shorter, or equal to the cut subtree
    n_plus = {}
    n_minus = {}
    n_0 = {}
    for child, size in all_sizes.items():
        if size > cut_size:
            n_plus[child] = size
        elif size < cut_size:
            n_minus[child] = size
        elif size == cut_size:
            n_0[child] = size


    ## case 1: there are no subrees bigger or smaller
    if len(n_plus)==0 or len(n_minus)==0:
        # if no options of correct length exist, exit
        if len(n_0) == 0:
            return 
        # else pick one at random
        subtree = random.choice(list(n_0.keys()))
        return subtree,subtree.parent
    
    ## case 2: n_plus,n_minus both exist
    # handled separately for clarity
    subtree = sf_weigthed_selection(all_sizes,n_minus,n_0,n_plus,cut_size)
    
    return subtree, subtree.parent

def sf_weigthed_selection(all_sizes,n_minus,n_0,n_plus,cut_size):
    """ 
    handles the complex weigthed selction of second crossover point for size_fair selection
    in the case where there are subtrees of size both larger and smaller the subtree recived
    """

    # we need the mean size difference w.r.t cut subtree, for both n_plus and n_minus
    mean_plus = np.mean(list(n_plus.values()))-cut_size
    mean_minus = cut_size - np.mean(list(n_minus.values()))
    
    # lists of all avaliable lenghts (+ cut_size)
    plus_lens=list(set(n_plus.values()))
    minus_lens=list(set(n_minus.values()))

    #choose from which dict to sample according to the following probabilities
    if len(n_0)!= 0:
        p_0 = 1/cut_size
    else: 
        p_0 = 0
    
    p_plus = (1-p_0)/(len(plus_lens)*(1+(mean_plus/mean_minus)))
    
    p_minus = (1 - p_0 - (p_plus*len(plus_lens)))/ len(minus_lens)       

    # prepare the list of subtree lengths and the probability of picking each length
    weights = [p_minus] * len(minus_lens) + [p_0] + [p_plus] * len(plus_lens)
    lengths = minus_lens + [cut_size] + plus_lens

    # pick a length
    sub_len = random.choices(lengths, weights=weights)[0]
    # pick a subtree of that length
    candidate_subtrees = [n for n,size in all_sizes.items() if size == sub_len]
    subtree = random.choice(candidate_subtrees)
    return subtree



def size_fair_crossover(parent1, parent2, max_depth):
    """ 
    Size-fair selection reduces bloat by looking for similar subtrees to do crossover
    """
    # Make copies of the parents to avoid modifying them directly
    child1 = deepcopy(parent1)
    child1.fitness = None

    # arbitrary choice of max numebr of iterations
    max_iter=500
    i=0
    found=None
    
    while not found and i<max_iter:
        # Select random crossover point in parent1
        crossover_node1,dangle1 = select_subtree(child1)
        residual_depth = max_depth - crossover_node1.depth
        # try to find size-fair equivalent in parent 2; if not select another crossover point in parent1
        found = sf_select_second_crossover(parent2,crossover_node1,residual_depth)
        i+=1
    
    if i == max_iter:
        raise RuntimeError('Max num of iterations to find crossover point exceed')
    
    # if size-fair crossover points are found, perform the crossover
    crossover_node2,dangle2 = found
    child1 = replace_subtree(child1,dangle1, crossover_node1, crossover_node2)

    return child1



################################ MUTATION ##############################################
def subtree_mutation(tree,function_set,terminal_set,operator_arities,p_op,p_ter,max_depth):
    '''
    Simple subtree mutation. The only constraint is on the depth of the mutated subtree, which must be <= max_depth
    '''
    # pick a random node on which perform a mutation
    all_nodes = [node for node in PreOrderIter(tree)]
    graft = random.choice(all_nodes)
    
    # compute how big the new subtree on graft can be
    residual_depth = max_depth - graft.depth

    # create a new subtree, and graft it onto the graft node
    new_branch = create_random_tree(residual_depth,function_set,terminal_set,operator_arities,p_op,p_ter)
    tree = replace_subtree(tree,graft.parent, graft, new_branch)
    
    return tree