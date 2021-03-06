

from neurotune import evaluators
from neurotune import optimizers
from neurotune import utils
import pprint
from pyelectro import analysis
from collections import OrderedDict

import sys

sys.path.append("..")

from c302Analysis import Data_Analyser
from c302Evaluators import EnhancedNetworkEvaluator
    
from SineWaveNetworkController import SineWaveNetworkController
    
if __name__ == '__main__':

    sim_vars = OrderedDict([('amp',              15),
                            ('amp_increment',    5),
                            ('period',           125),
                            ('period_increment', 50),
                            ('offset',           -10),
                            ('offset_increment', 5)])
               
    print sim_vars.keys()
    
    swc = SineWaveNetworkController('wave', 2)
    
               
    min_constraints = [4,  -5,   50,  0,   -12, -20]
    max_constraints = [22, 20,   230, 160, 15,  20]
    

    times, volts = swc.run_individual(sim_vars, True, False, prefix="Orig: ")
    
 

    analysis_var={'peak_delta':0,'baseline':0,'dvdt_threshold':0, 'peak_threshold':0}


    
    # The output of the analysis will serve as the basis for model optimization:
    pp = pprint.PrettyPrinter(indent=4)
    

             
    weights={'wave_0:average_maximum': 1,
             'wave_0:average_minimum': 1,
             'wave_0:mean_spike_frequency': 10,
             'wave_1:average_maximum': 1,
             'wave_1:average_minimum': 1,
             'wave_1:mean_spike_frequency': 10}
             
    weights={'wave_0:average_maximum': 1,
             'wave_0:average_minimum': 1,
             'wave_1:average_maximum': 1,
             'wave_1:average_minimum': 1,
             'wave_0;wave_1;phase_offset' : 10}
             
    surrogate_analysis=Data_Analyser(volts,
                                               times,
                                               analysis_var,
                                               start_analysis=0,
                                               end_analysis=1000)
                                               
    surrogate_targets = surrogate_analysis.analyse(targets=weights)
    
    pp = pprint.PrettyPrinter(indent=4)
    print("Surrogate analysis")
    pp.pprint(surrogate_targets)
    
    surrogate_targets['wave_0;wave_1;phase_offset'] = 180
    
    #make an evaluator
    my_evaluator=EnhancedNetworkEvaluator(controller=swc,
                                            analysis_start_time=0,
                                            analysis_end_time=1000,
                                            parameters=sim_vars.keys(),
                                            analysis_var=analysis_var,
                                            weights=weights,
                                            targets=surrogate_targets)
    
    population_size =  100
    max_evaluations =  700
    num_selected =     10
    num_offspring =    10
    mutation_rate =    0.9
    num_elites =       3

    #make an optimizer
    my_optimizer = optimizers.CustomOptimizerA(max_constraints,
                                             min_constraints,
                                             my_evaluator,
                                             population_size=population_size,
                                             max_evaluations=max_evaluations,
                                             num_selected=num_selected,
                                             num_offspring=num_offspring,
                                             num_elites=num_elites,
                                             mutation_rate=mutation_rate,
                                             seeds=None,
                                             verbose=True)
    
    #run the optimizer
    best_candidate, fitness = my_optimizer.optimize(do_plot=False, seed=123456)
    
    keys = sim_vars.keys()
    fittest_sim_vars = {}
    for i in range(len(best_candidate)):
        fittest_sim_vars[keys[i]] = best_candidate[i]
        
    print(sim_vars)
    print(fittest_sim_vars)

    fit_times, fit_volts = swc.run_individual(fittest_sim_vars, True, False)

    fit_analysis=Data_Analyser(fit_volts,
                                          fit_times,
                                          analysis_var,
                                          start_analysis=0,
                                          end_analysis=1000)

    fit_anal = fit_analysis.analyse(targets=weights)

    print("Surrogate analysis")
    pp.pprint(surrogate_targets)

    print("Fittest analysis")
    pp.pprint(fit_anal)

    utils.plot_generation_evolution(sim_vars.keys(), sim_vars)
    
    
