###DFA TRIALS

from .data_structure_definitions import *
from .utils_oss.DFA import *

def printGraphicLibDfa(myDfa, fp):
  g=graphviz.Digraph(format='pdf')
  g.body.extend(['rankdir=TB'])
  
  for s in myDfa.states:
    if s != -1 and s != (-1, -1):
      g.node(str(s), shape='circle')
    
  for s in myDfa.states:
    for alpha in myDfa.alphabet:
      if myDfa.delta(s, alpha) != -1 and myDfa.delta(s, alpha) != (-1, -1):
        g.edge(str(s), str(myDfa.delta(s, alpha)), label = alpha)
        # print str(s), str(myDfa.delta(s, alpha)), alpha
      
  file=g.render(filename=fp)	  
  print(file)
  
def hackyAlphabet(doof1, doof2):
  alphabet = []
  for k,v in doof1.transitions.items():
    if k[1] not in alphabet:
      alphabet.append(k[1])
  for k,v in doof2.transitions.items():
    if k[1] not in alphabet:
      alphabet.append(k[1])
  alphabet.sort()
  return alphabet
    
def makeOfficialDfa(doof, alphabet):
  
  states = doof.states
  states.append(-1) 
  delta = lambda q,c : doof.transitions[(q, c)] if ((q,c) in doof.transitions) else -1
  start = doof.initialStates[0]
  accepts = doof.finalStates
  myDfa = DFA(states, alphabet, delta, start, accepts)
  # myDfa.pretty_print()
  return myDfa
