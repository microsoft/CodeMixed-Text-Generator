###LATTICE OPERATIONS

from .data_structure_definitions import *

def trimTrapStates(doof):
  flag = 1
  while flag == 1:
    flag = 0
    statesToDelete = []
    dict_items = set([t[0][0] for t in doof.transitions.items()])
    for i, state in enumerate(doof.states):
      if state not in dict_items:
      # if len([0 for (k, v) in dict_items if k[0] == state]) == 0:
        if state != doof.engEnd and state != doof.mixEnd and state != doof.hinEnd and state not in doof.finalStates:
          statesToDelete.append(state)
          flag = 1
    
    for state in statesToDelete:
      doof.deleteState(state)
      
def mergeEquivalentStates(doof):
  flag = 1
  while flag == 1:
    flag = 0
    toMerge = []
    
    for state1 in doof.states:
      for state2 in doof.states:
        if state1 != state2: 
          transitions1 = [(k[1], v) for k,v in doof.transitions.items() if k[0] == state1]
          transitions2 = [(k[1], v) for k,v in doof.transitions.items() if k[0] == state2]
          if transitions1!=[] and transitions2!=[] and transitions1 == transitions2:
            toMerge.append((state1, state2))
            flag = 1
            
    for pair in toMerge:
      if pair[0] in doof.states and pair[1] in doof.states:
        # print 'deleting these:'
        # print pair[0], pair[1]
        doof.mergeStates(pair[0], [pair[1]])
 
def removeUselessStates(doof):
  statesToRemove = []
  for state in doof.states:
    transIn = {k: v for k, v in doof.transitions.items() if v == state}
    transOut = {k: v for k, v in doof.transitions.items() if k[0] == state}
    
    if state != 0 and len(transIn) == 0:
      statesToRemove.append(state)
      
    if len(transIn) == 1 and len(transOut) ==  1:
      keys_in = list(transIn.keys())
      keys_out = list(transOut.keys())
      values_out = list(transOut.values())
      doof.addTransition(keys_in[0][0], keys_in[0][1][:-2]+" "+keys_out[0][1], values_out[0])
      del doof.transitions[keys_in[0]]
      del doof.transitions[keys_out[0]]
      statesToRemove.append(state)
      
  for state in statesToRemove:
    doof.deleteState(state)

def removeDollarTransitions(doof):
  
  dollarTransitions = {k:v for k,v in doof.transitions.items() if k[1] == "$_h" or k[1] == "$_e"}
  for k,v in dollarTransitions.items():
    transitionsToSink = {kk:vv for kk,vv in doof.transitions.items() if vv == v}
    if len(transitionsToSink) == 1:
      del doof.transitions[k]
      doof.mergeStates(k[0], [v])
    else:
      print("null transition between" + str(k[0]) + "and" + str(v) + "could not be removed") 
  
def removeUnreachableStates(doof):  

  flag = 1
  while flag == 1:
    flag = 0
    statesToDelete = []
    for state in doof.states:
      if len({k: v for k, v in doof.transitions.items() if v == state}) == 0:
        if state != doof.initialStates[0]:
          statesToDelete.append(state)
          flag = 1
    
    for state in statesToDelete:
      doof.deleteState(state)
  
    