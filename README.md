# Evolving Constructions for Balanced, Highly Nonlinear Boolean Functions
This project aims to reproduce the results from the paper [Evolving Constructions for Balanced, Highly Nonlinear Boolean Functions](https://arxiv.org/abs/2202.08743)
```bib
@misc{carlet2022evolvingconstructionsbalancedhighly,
      title={Evolving Constructions for Balanced, Highly Nonlinear Boolean Functions}, 
      author={Claude Carlet and Marko Djurasevic and Domagoj Jakobovic and Luca Mariot and Stjepan Picek},
      year={2022},
      eprint={2202.08743},
      archivePrefix={arXiv},
      primaryClass={cs.NE},
      url={https://arxiv.org/abs/2202.08743}, 
}
```

## Project structure
 - `GP_classes.py`: contains the `TreeNode` and `Seed`classes, plus some useful functions such as `print_tree` and `display_truth_table`, which provide a visual representation of the trees and truth tables respectively.
 - `GP_classes.py`: contains all selection, crossover, and mutation functions.
 - `GP_evaluation.py`: contains functions used in the fitness evaluation of the constructions; this includes Objectives and Fitnesses
 - `GP_seeds_pool.py`: seeds for experiments are picked uniformly at random from a `seeds_pool` of truth tables; this file includes functions used for generating the `seeds_pool` with the correct number of variables `n_old_vars`. This is done by exhaustive search for `n_old_vars<5`, otherwise by taking the top 10% results from previous experiments.
 - `experiment.py`: allows you to run an experiment.
 - `GP_setup_eval.py`: provides functions used for evaluating the results of a full population evolution
 - 
## Usage
To create an environment with the required packages:
```sh
# Conda packages
conda create --name NLbooleans --file requirements.txt
# Pip packages
pip install anytree tqdm
```

To run a full experiment you can execute `experiment.py` as follows:

```sh
python experiment.py --pop_size 500 --max_depth 5 --n_new_vars 2 --n_old_vars 4 --n_seeds 4 --n_groups 4 --obj obj1 --fit fit1 --max_evals 10000
```

Results will be saved as a pickle file in `/experiments`.

