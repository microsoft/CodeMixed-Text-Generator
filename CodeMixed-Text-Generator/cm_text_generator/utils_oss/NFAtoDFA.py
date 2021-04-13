# NFAtoDFA.py
#
# Author: Stefan Mendoza
# Date: 2 October 2015
# Email: stefanmendoza.dev@gmail.com

import string
import sys

'''
Global variables
'''
alphabet = []
initial_state_nfa = []
table_nfa = {}
states_dfa = []
table_dfa = {}


'''
Flattens a nested listed into a single-dimension list
'''
def flatten(l):
    result = []
    for elem in l:
        if hasattr(elem, "__iter__") and not isinstance(elem, basestring):
            result.extend(flatten(elem))
        else:
            result.append(elem)
    return(result)


'''
Generates the resulting list of states from running eClosure on a state
'''
def eClosure(state):
    
    finalSet = [singleState for result in map(lambda s: table_nfa.get((s, 'E')), state) for singleState in result]
    
    if set(state) == set(finalSet):
        return(state)
    else:
        currentSet = finalSet
        while currentSet != []:
            currentSet = flatten(map(lambda s: table_nfa.get((s, 'E')), currentSet))
            if set(finalSet) == set(finalSet).union(set(currentSet)):
                currentSet = []
            finalSet += currentSet
    return(sorted(list(set(state).union(finalSet))))


'''
Adds a state + transitions to the DFA
'''
def createEntry(s):
    global table_dfa
    moves = move(s)
    for i in range(0, len(alphabet) - 1):
        if moves[i] == []:
            table_dfa[(str(s), alphabet[i])] = []
        else:
            table_dfa[(str(s), alphabet[i])] = states_dfa.index(eClosure(moves[i])) + 1


'''
Returns a list of n lists where n is the length of the alphabet (sans the empty
string) and each list corresponds to (q, i) where q is the state passed to the
function and i is the input character of the alphabet.

NOTE: The list returned corresponds to the order that the alphabet was given.
If the alphabet is [c, a, b] the result will be:
[ [states from move on c], [states from move on a], [states from move on b]]
'''
def move(state):
    a = alphabet[:]
    a.remove('E')
    return(map(flatten, [map(lambda s: table_nfa.get((s, i)), state) for i in a]))


'''
Prints out a list of states as {1, 2, 3, 4} instead of as [1, 2, 3, 4]
'''
def listToSetString(state):
    if state == []:
        return("{}")
    else:
        setString = "{"
        for i in range(0, len(state) - 1):
            setString += str(state[i]) + ", "
        setString += str(state[len(state) - 1]) + "}"
        return(setString)


'''
Prints out a transition table
'''
def printTransitionTable(states, initial_state, final_states, table):
    # Display the header for the transition table
    print("\nInitial State: " + listToSetString(initial_state))
    print("Final States: " + listToSetString(final_states))
    print("State"),
    for i in range(0, len(alphabet) - 1):
        print("\t" + str(alphabet[i])),
    print

    # Display the states with their transitions
    for i in states:
        print(str(states.index(i) + 1)),
        for j in range(0, len(alphabet) - 1):
            transition = table.get((str(i), alphabet[j]))
            if transition == []:
                print("\t" + "{}"),
            else:
                print("\t" + "{" + str(table.get((str(i), alphabet[j]))) + "}"),
        print
    print

def main_as_function(ini_state_nfa, fin_states_nfa, tot_states_nfa, alpha_nfa, tab_nfa):
  global alphabet
  global initial_state_nfa
  global table_nfa
  global states_dfa
  global table_dfa
  
  alphabet = []
  initial_state_nfa = []
  table_nfa = {}
  states_dfa = []
  table_dfa = {}

  # Populate state information
  initial_state_nfa = ini_state_nfa
  final_states_nfa = fin_states_nfa
  totalStates = tot_states_nfa
  alphabet = alpha_nfa
  table_nfa = tab_nfa

  stack = [eClosure([initial_state_nfa])]
  
  # Generate DFA states
  # print("\nE-closure(IO) = " + listToSetString(eClosure([initial_state_nfa])) + " = 1")
  while stack != []:
      current = stack[0]
      # print "Stack[0] is: ", stack[0]
      if current not in states_dfa:
          states_dfa.append(current)
          # print "Added to dfa"
          moves = move(current)
          # print "Moves: ", moves
          for i in range(0, len(alphabet) - 1):
              e = eClosure(moves[i])
              # print "Moving by ", alphabet[i], "gives", e
              if moves[i] != [] and e not in states_dfa:
                  stack.append(e)
                  # print "appended to stack"
      stack = [s for s in stack[1:] if s != []]
      
  # print 'DFA states:', states_dfa

  # Print steps and generate transition table
  for state in states_dfa:
      moves = move(state)
      # print("\nMark"),
      # print(states_dfa.index(state) + 1)
      for i in range(0, len(alphabet) - 1):
          if moves[i] != []:
                  # print(listToSetString(state) + " --- " + alphabet[i] + " --> " + listToSetString(moves[i]))
                  e = eClosure(moves[i])
                  # print("E-closure" + listToSetString(moves[i]) + " = " + listToSetString(e) + " ="),
                  # print(states_dfa.index(e) + 1)
      createEntry(state)

  # Determine the inital states for the DFA
  initial_state_dfa = []
  for i in range(0, len(states_dfa)):
      if initial_state_nfa in states_dfa[i]:
          initial_state_dfa = [(i + 1)]
          break

  # Determine the final states for the DFA
  final_states_dfa = []
  for i in range(0, len(states_dfa)):
      if set(states_dfa[i]).intersection(set(final_states_nfa)):
          final_states_dfa.append(i + 1)

  # printTransitionTable(states_dfa, initial_state_dfa, final_states_dfa, table_dfa)        
  return (states_dfa, initial_state_dfa, final_states_dfa, table_dfa)


'''
Takes an NFA as standard input with the following format:

Initial State: {i}
Final States: {i1, i2, i3}
Total States: integer
State   input1  input2  input3  ... inputn
1         s1       s2     s3    ...   sn
.
.
.
n         s1       s2     s3    ...   sn

where s_i corresponds to set of states resulting from  moving on input_i from
the corresponding state. It is assumed that 'E' will be the empty string.
'''
def main():
    global alphabet
    global initial_state_nfa
    global table_nfa
    global states_dfa
    global table_dfa

    # Parse out state information
    initial_state_nfa = list(eval(sys.stdin.readline().strip().split(':')[1]))[0]
    print(initial_state_nfa)
    final_states_nfa = list(eval(sys.stdin.readline().strip().split(':')[1]))
    print(final_states_nfa)
    totalStates = int(sys.stdin.readline().strip().split(':')[1])
    print(totalStates)
    alphabet = sys.stdin.readline().strip().split('\t')[1:]
    print(alphabet)

    # Create the transition table for the NFA
    for i in range(0, totalStates):
        state_info = sys.stdin.readline().strip().split('\t')
        for i in range(1, len(alphabet) + 1):
            s = eval(state_info[i])
            if s == {}:
                table_nfa[(int(state_info[0]), alphabet[i - 1])] = []
            else:
                table_nfa[(int(state_info[0]), alphabet[i - 1])] = list(s)

    stack = [eClosure([initial_state_nfa])]

    # Generate DFA states
    print("\nE-closure(IO) = " + listToSetString(eClosure([initial_state_nfa])) + " = 1")
    while stack != []:
        current = stack[0]
        if current not in states_dfa:
            states_dfa.append(current)
            moves = move(current)
            for i in range(0, len(alphabet) - 1):
                e = eClosure(moves[i])
                if moves[i] != [] and e not in states_dfa:
                    stack.append(e)
        stack = [s for s in stack[1:] if s != []]

    # Print steps and generate transition table
    for state in states_dfa:
        moves = move(state)
        print("\nMark"),
        print(states_dfa.index(state) + 1)
        for i in range(0, len(alphabet) - 1):
            if moves[i] != []:
                    print(listToSetString(state) + " --- " + alphabet[i] + " --> " + listToSetString(moves[i]))
                    e = eClosure(moves[i])
                    print("E-closure" + listToSetString(moves[i]) + " = " + listToSetString(e) + " ="),
                    print(states_dfa.index(e) + 1)
        createEntry(state)

    # Determine the inital states for the DFA
    initial_state_dfa = []
    for i in range(0, len(states_dfa)):
        if initial_state_nfa in states_dfa[i]:
            initial_state_dfa = [(i + 1)]
            break

    # Determine the final states for the DFA
    final_states_dfa = []
    for i in range(0, len(states_dfa)):
        if set(states_dfa[i]).intersection(set(final_states_nfa)):
            final_states_dfa.append(i + 1)

    printTransitionTable(states_dfa, initial_state_dfa, final_states_dfa, table_dfa)

if __name__ == "__main__":
    main()
