###TO MAKE WORD LATTICE FOR EMBEDDED-MATRIX MODEL

import uuid

from .data_structure_definitions import *
from .helper_functions import *
from .play_with_dfa import *
from .utils_oss.NFAtoDFA import *
  
def makeEmLattice(node, grammar, model):
  
  node.doof = dfa()
  node.counterpart.doof = dfa()
  node.fullySwitchable = False

  if node.token != 'XXXXX':
    a = node.doof.addState()
    b = node.doof.addState()
    node.doof.addTransition(a, node.token+"_"+node.language[0], b)
    
    c = node.counterpart.doof.addState()
    d = node.counterpart.doof.addState()
    node.counterpart.doof.addTransition(c, node.counterpart.token+"_"+node.counterpart.language[0], d)

    cond = False
  
  else:
    cond = True
    
    for child in node.children:
      makeEmLattice(child, grammar, model)
      node.doof.mergeDfaSeries(child.doof)
      cond = cond and child.fullySwitchable
      
    for child in node.counterpart.children:
      node.counterpart.doof.mergeDfaSeries(child.doof)
  
  if model.nest == False:  
    if node.label in model.switchLabels and (cond == False or grammar[node.ruleNum].languageAgnostic == False):
      node.doof = mergeParallelViaNfa(node.doof, node.counterpart.doof)
      
  else:
    if node.label in model.switchLabels:
      node.doof = mergeParallelViaNfa(node.doof, node.counterpart.doof)
      node.counterpart.doof = node.doof
      
  node.fullySwitchable = (cond and grammar[node.ruleNum].languageAgnostic)\
                              or (node.label in model.switchLabels)
                              
  # node.doof.printGraphicDfa("output\\small\\"+str(uuid.uuid4()))
      
def mergeParallelViaNfa(dfa1, dfa2):
 
  firstStart = dfa1.initialStates[0]
  firstEnd = dfa1.finalStates[0]
  secondStart = dfa1.nextIndex
  secondEnd = secondStart + dfa2.finalStates[0]
  
  alpha = hackyAlphabet(dfa1, dfa2)
  alpha.append('E')
  
  dfa1.mergeDfa(dfa2)
  
  total_states_nfa = len(dfa1.states) 
  initial_state_nfa = dfa1.states.index(dfa1.initialStates[0]) + 1
  final_states_nfa = [dfa1.states.index(x) + 1 for x in dfa1.finalStates]
  
  nfa_transitions = {}
  
  for state in dfa1.states:
    for letter in alpha:
      if (state, letter) in dfa1.transitions:
        nfa_transitions[(dfa1.states.index(state) + 1, letter)] = [dfa1.states.index(dfa1.transitions[(state, letter)]) + 1]
      else:
        nfa_transitions[(dfa1.states.index(state) + 1, letter)] = []
  
  nfa_transitions[(dfa1.states.index(firstStart) + 1, 'E')].append(dfa1.states.index(secondStart) + 1)
  nfa_transitions[(dfa1.states.index(secondEnd) + 1, 'E')].append(dfa1.states.index(firstEnd) + 1)
  
  (states_dfa, initial_state_dfa, final_states_dfa, table_dfa) = main_as_function(initial_state_nfa, final_states_nfa, total_states_nfa, alpha, nfa_transitions)
  
  mergedDfa = dfa()
  mergedDfa.states = [states_dfa.index(i) for i in states_dfa]
  mergedDfa.initialStates = [initial_state_dfa[0]-1]
  mergedDfa.finalStates = [i-1 for i in final_states_dfa]
  mergedDfa.nextIndex = max(mergedDfa.states) + 1
  
  mergedDfa.transitions = {}
  for i in states_dfa:
    for j in range(len(alpha)-1):
      transition = table_dfa.get((str(i), alpha[j]))
      if transition != []:
        mergedDfa.transitions[(states_dfa.index(i), alpha[j])] = transition - 1
  if len(mergedDfa.finalStates) > 1:
    mergedDfa.mergeStates(mergedDfa.finalStates[0], mergedDfa.finalStates[1:])
  
  return mergedDfa
  

  