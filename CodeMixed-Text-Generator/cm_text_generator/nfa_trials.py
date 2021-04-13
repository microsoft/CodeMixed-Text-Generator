###NFA TRIALS

from data_structure_definitions import *
from .utils_oss.NFAtoDFA import *
from play_with_dfa import *

def fillEpsilonTransitions(node, nfa_transitions, states, secondStart):
  if states.index(node.counterpart.emDfaStart+secondStart) + 1 not in nfa_transitions[(states.index(node.emDfaStart) + 1, 'E')]:
    nfa_transitions[(states.index(node.emDfaStart) + 1, 'E')].append(states.index(node.counterpart.emDfaStart+secondStart) + 1)
  if states.index(node.emDfaEnd) + 1 not in nfa_transitions[(states.index(node.counterpart.emDfaEnd+secondStart) + 1, 'E')]:
    nfa_transitions[(states.index(node.counterpart.emDfaEnd+secondStart) + 1, 'E')].append(states.index(node.emDfaEnd) + 1)
  for child in node.children:
    fillEpsilonTransitions(child, nfa_transitions, states, secondStart)

def mergeForNesting(dfa1, dfa2, root):
 
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
  
  # nfa_transitions[(dfa1.states.index(firstStart) + 1, 'E')].append(dfa1.states.index(secondStart) + 1)
  # nfa_transitions[(dfa1.states.index(secondEnd) + 1, 'E')].append(dfa1.states.index(firstEnd) + 1)
  fillEpsilonTransitions(root, nfa_transitions, dfa1.states, secondStart)
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
  
  mergedDfa.printGraphicDfa('output\lattice')
  return mergedDfa

def updateEndPoints(node, delta, stepDown):
  node.emDfaStart = node.emDfaStart + delta
  if delta > 0:
    node.emDfaStart = node.emDfaStart - stepDown
  node.emDfaEnd = node.emDfaEnd + delta
  for child in node.children:
    if stepDown == 0:
      updateEndPoints(child, delta, stepDown)
    else: 
      if node.children.index(child) == 0:
        stepDown = 1
      else:
        stepDown = 0
      updateEndPoints(child, delta, stepDown)
  
def makeEggEmLattice(node, grammar, lang1, lang2):
  
  node.doof = dfa()

  if node.token != 'XXXXX':
    a = node.doof.addState()
    b = node.doof.addState()
    node.doof.addTransition(a, node.token+"_"+lang1, b)
    if node.canSwitch == 1:
      node.doof.addTransition(a, node.counterpart.token+"_"+lang2, b)
    node.emDfaStart = a
    node.emDfaEnd = b

  else:
    # cond = True
    for child in node.children:
      makeEggEmLattice(child, grammar, lang1, lang2)
      delta = node.doof.nextIndex
      node.doof.mergeDfaSeries(child.doof)
      updateEndPoints(child, delta, 1)
    node.emDfaStart = node.doof.initialStates[0]
    node.emDfaEnd = node.doof.finalStates[0]
      # cond = cond and child.fullySwitchable
    # if (cond == False and node.canSwitch == 1) or (grammar[node.ruleNum].languageAgnostic == False):
      # node.doof.addTransition(node.doof.initialStates[0], surfaceForm(node.counterpart), node.doof.finalStates[0])


  


   