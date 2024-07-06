from anytree import Node, PreOrderIter, RenderTree
import operator
from itertools import product
import random
import numpy as np




class CustomOperator:
    '''
    Class for all the binary operations that are not included in the Operator class
    '''
    @staticmethod
    #this is vestigial; IF is evaluatued without calling this for efficiency 
    def if_(cond, a, b):
        a_value = a() if callable(a) else a
        b_value = b() if callable(b) else b
        return a_value if cond else b_value
    
    @staticmethod
    def and2_(a,b):
        return a and not b
    
    @staticmethod
    def xnor_(a,b):
        return not a ^ b


class Seed:
    '''
    The seeds are used as part of a construction.
    Each seed has the following attributes:
     - a name (usually 'f1','f2',..,'f3')
     - a truth table, used in the evaluation of a construction
     - a list of variable names
    '''
    def __init__(self,name, truth_table,variables): #, group:seedGroup):
        self.name = name
        self.truth_table = truth_table
        #self.group = group
        self.variables = variables

    def __str__(self):
        '''
        The string that represents the seed
        '''
        return self.name
    
    def evaluate_seed(self,ground_truth):
        '''
        Returns the value of the output of the seed for a given input
        '''
        seed_truth = tuple(ground_truth[var] for var in self.variables)
        return self.truth_table[seed_truth]



def create_groups(truth_tables,seeds):
    '''
    From a list of truth tables and some seeds, split the list of truth tables in groups, so that new seeds can be generated
    by swapping the truth table of the given seeds
    Note that the number of truth tables provided should be a multiple of the number of seeds
    '''
    group_size = len(seeds)
    # Split the list into groups
    generate_group = lambda tts,seeds: {seed:tt for seed,tt in zip(seeds,tts)}
    groups = tuple(generate_group(truth_tables[i:i + group_size],seeds) for i in range(0,len(truth_tables), group_size))
    return groups


def create_seeds(truth_tables,n_seeds,seed_vars):#,n_groups=4):
    return tuple(Seed(f'f{i+1}',truth_tables[i],seed_vars) for i in range(n_seeds))



# inherit the anytree class
class TreeNode(Node):
    '''
    The class used for the trees representing the construction. It inherits from the 'anytree' Node class.
    
    Each node has the following attributes (only relevant atributes listed):
     - a name, which can be any type of of object. In our case it may be a string for new variable, 
       a Seed for seed functions, or an operator for non-leaf nodes
     - a parent node
     - a tuple of children nodes
     - a depth, which represents the depth of the node with respect to the root (0 if the node is a root)
     - a fitnees value, which is used during the evolution
     - a nonlinearity value, which is used during final evaluation
    '''
    def __init__(self, name, parent=None, children=None, **kwargs):
        super().__init__(name, parent, children, **kwargs)
        self.fitness=None
        self.NL=None
        
    def size(self):
        '''
        Number of nodes in the (sub)tree rooted on the node
        '''
        return sum(1 for _ in PreOrderIter(self))
    def compute_depth(self):
        '''
        depth of the (sub)tree rooted on the node
        '''
        max_depth = 0
        
        for node in PreOrderIter(self):
            depth = node.depth + 1 
            # Update the maximum depth if the current depth is greater
            max_depth = max(max_depth, depth)

        # take the depth of the subtree w.r.t self, not to the root of the parent tree
        max_depth-=self.depth    
        return max_depth
    
    def evaluate_tree(self,ground_truth,variable_set,function_set,operators):
        """
        Given a dict of values for each variable ( 'ground_truth'), produces the truth table of the (sub)tree rooted on the node.
        """ 
        ## Node in terminal_set:
        # node can be a new variable 
        if self.name in variable_set:
            # read the value of the variable in 'ground_truth'
            return ground_truth[self.name]

        # node can be a seed function 
        if isinstance(self.name, Seed):
            # compute the output of the seed for thgiven input
            seed = self.name
            return seed.evaluate_seed(ground_truth)

        ## Node in fucntion_set: evaluate the trees on the children
        children = self.children

        if self.name in function_set and self.name != 'IF':
            # recursively get the output of the children nodes for the given input
            children_values = tuple(child.evaluate_tree(ground_truth,variable_set,function_set,operators) for child in children)
            # compute the output of the current node using the children values as inputs
            node_value = operators[self.name](*children_values)
            return node_value
            
        # evaualuate IF separately so that we don't eval branches if not needed
        if self.name == 'IF':
            cond, op1, op2  = children
            cond_value =  cond.evaluate_tree(ground_truth,variable_set,function_set,operators)
            node_value = op1.evaluate_tree(ground_truth,variable_set,function_set,operators) if cond_value else op2.evaluate_tree(ground_truth,variable_set,function_set,operators)
            return node_value
        
        else:
            raise ValueError(f'Cannot evaluate node {self.name} of type {type(self.name)}')
        
    def truth_table(self,variable_set,function_set,operators): #remember to pass variable_set not terminal_set
        '''
        Returns the truth table associated with the construction. The truth table is stored as a dictionary.
        '''
        truth_table={}
        for input in product((0, 1), repeat=len(variable_set)):
            ground_truth = {var:int(value) for var,value in zip(variable_set,input) }
            # compute the output of the tree for all possible combinations of inputs
            truth_table[input] = int(self.evaluate_tree(ground_truth,variable_set,function_set,operators))
        return truth_table


def create_random_tree(max_depth,function_set,terminal_set,operator_arities,p_op,p_ter):
    '''
    Generates a random tree of maximus depth max_depth, with leaves in the terminal_set and inner nodes 
    which are operators
    '''

    # Generation is done recursively
    # pick the type of node: from function_set with probability p_op, from terminal_set with probability p_ter
    node_type = random.choices([function_set,terminal_set],weights=[p_op,p_ter])[0]

    # if generating a leaf (at max_depth all nodes are leaves) pick at random from terminal_set
    if max_depth == 1 or node_type == terminal_set:  
        return TreeNode(random.choice(terminal_set))
    
    # if generating an inner node pick at random from function_set
    else:
        # create new node
        node_value = np.random.choice(function_set)
        node = TreeNode(node_value)

        # create children nodes recursively (decrease max_depth)
        arity = operator_arities[node_value]
        for _ in range(arity):
            child = create_random_tree(max_depth -1,function_set,terminal_set,operator_arities,p_op,p_ter)
            child.parent = node
        return node


def print_tree(tree):
    """ 
    Provides a graphical representation of the tree
    """
    for pre, _ , node in RenderTree(tree):
        print("%s%s" % (pre, node.name))


def display_truth_table(truth_table,variable_set):
    """ 
    Provides a visual representation of a truth table produced by either a tree or a seed 
    """
    # Header
    headers = " | ".join([str(leaf) for leaf in variable_set]) + " || truth"
    print('| '+headers)
    print('-' * len(headers)+ '--')
    for inputs,output in truth_table.items():
        
        values_str = " |  ".join(str(value) for value in inputs)
        print(f"|  {values_str} ||   {output}")
    print('-' * len(headers) + '--')
    return 