###GRAMMAR INFERENCE

from .data_structure_definitions import *

def ruleEnlister(root, grammar):
  if root.token=="XXXXX":
    cond=False
    for rule in grammar: ##check false/true
      if (rule.lhs.nonTerminal==root.label and len(rule.rhs)==len(root.children)):
        #print "Using old rule!"
        cond=True
        for counter in range(len(rule.rhs)):
          if(rule.rhs[counter].nonTerminal!=root.children[counter].label or rule.rhs[counter].index!=root.children[counter].repeatIndex):
            cond=False          
        if cond==True:
          root.ruleNum=rule.ruleNum

    if(root.ruleNum==-1):
      #print "Making new rule!", str(len(grammar))
      lhs=grammarPoint(root.label, -1, -1)
      
      rhs=[]
      for child in root.children:
        rhs.append(grammarPoint(child.label, child.repeatIndex, root.children.index(child)))
       
      grammar.append(grammarRule(len(grammar), lhs, rhs))

      root.ruleNum=len(grammar)-1   

    for child in root.children:
      ruleEnlister(child, grammar)
 
def projectHindiRules(hinRoot, grammar):
  if hinRoot.token=="XXXXX":
    # print "\nLABEL: ", hinRoot.label, " ", str(hinRoot.ruleNum)
    for child in hinRoot.children:
      for count in range(len(grammar[hinRoot.ruleNum].rhs)):
        #print "(", child.label, grammar[hinRoot.ruleNum].rhs[count].nonTerminal, child.repeatIndex, grammar[hinRoot.ruleNum].rhs[count].index, ")",

        if child.label==grammar[hinRoot.ruleNum].rhs[count].nonTerminal and \
         child.repeatIndex==grammar[hinRoot.ruleNum].rhs[count].index:
          #print "index assigned: ", ind
          grammar[hinRoot.ruleNum].rhs[count].hinRank=hinRoot.children.index(child)
          #print "incrementing..."

    for child in hinRoot.children:
      projectHindiRules(child, grammar)       