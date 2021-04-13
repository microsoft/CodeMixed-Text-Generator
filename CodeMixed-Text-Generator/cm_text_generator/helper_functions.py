###HELPER FUNCTIONS

from .data_structure_definitions import *

#seems useless
def addDeterminers(hinRoot, engRoot, hinTokenList):
  if hinRoot.children!=[] and engRoot.children!=[]:
    # print "Checking", hinRoot.label, hinRoot.children[0].token
    if (engRoot.children[0].token=="the" or engRoot.children[0].token=="The"):
      # print "Bang bang"
      newIndex=len(hinTokenList)
      # print newIndex
      newElem=node(parent=hinRoot, token="", tokenNum=newIndex)
      
      newElem.alignments=[engRoot.children[0].tokenNum]
      newElem.counterpart=engRoot.children[0]
      newElem.label=engRoot.children[0].label
      newElem.parent=hinRoot
      newElem.language="Hindi"

      engRoot.children[0].alignments.append(newIndex)
      engRoot.children[0].counterpart=newElem
        
      hinTokenList.insert(insertIndex(hinRoot, hinTokenList), newElem)
      hinRoot.children.insert(0, newElem)
      # print "NOW"
      # hinRoot.printTree()

    for child in hinRoot.children:
      addDeterminers(child, child.counterpart, hinTokenList)

def ancestor(ances, kid):
  climber=kid
  while (climber!=ances and climber.label!="root"):
    climber=climber.parent 
  if(climber.label!="root"):
    return True
  return False

def checkRuleOrder(grammar):
  for rule in grammar:
    rule.languageAgnostic = True
    for point in rule.rhs:
      if point.engRank != point.hinRank:
        rule.languageAgnostic = False
  
#seems useless
def checkTreeStructures(hinRoot, engRoot, hinTokenList, engTokenList):
  if len(hinRoot.children)!=len(engRoot.children):
    print("Flattening at " + hinRoot.label + str(lowToken(hinRoot)) + ":" + str(highToken(hinRoot)))
    newChildrenList=[]
    flattenTreeNode(hinRoot, newChildrenList)
    compressTree(hinRoot, newChildrenList)

    newChildrenList=[]
    flattenTreeNode(engRoot, newChildrenList)
    compressTree(engRoot, newChildrenList)

    engRoot.children[0].label=hinRoot.children[0].label
    hinRoot.children[0].finalAlignment=engTokenList.index(engRoot.children[0])
    engRoot.children[0].finalAlignment=hinTokenList.index(hinRoot.children[0])
    hinRoot.children[0].counterpart=engRoot.children[0]
    engRoot.children[0].counterpart=hinRoot.children[0]  

  else:
    for child in hinRoot.children:
      checkTreeStructures(child, child.counterpart, hinTokenList, engTokenList)    
  
def closestCommonAncestor(root, node1, node2):
  cca=root
  newCCA=root.children[0]
  while(newCCA!=cca):
    cca=newCCA
    for child in cca.children:
      if ancestor(child, node1) and ancestor(child, node2):
        newCCA=child
  return cca

#seems useless
def compressTree(treeNode, tokenList):
  newToken=""
  newNonTerminal=""
  newAlignments=[]
  for child in tokenList:
    if newToken=="":
      newToken=child.token
      newNonTerminal=child.label
      newAlignments=child.alignments
    else:
      newToken=newToken+" "+child.token
      newNonTerminal=newNonTerminal+"+"+child.label
      newAlignments=newAlignments+list(set(child.alignments)-set(newAlignments))
      child.token="XX"
  
  tokenList[0].label=newNonTerminal
  tokenList[0].token=newToken
  tokenList[0].parent=treeNode
  tokenList[0].alignments=newAlignments
  treeNode.children=[tokenList[0]]  
  
def deleteNodeRecursive(currNode):
  parentNode=currNode.parent
  parentNode.children.remove(currNode)
  if len(parentNode.children)==0:
    deleteNodeRecursive(parentNode)
	
def equivalentNodes(treeNode1, treeNode2):
  if treeNode1.label=="root" and treeNode2.label=="root":
    return True
  if treeNode1.label==treeNode2.label and treeNode1.parent.ruleNum==treeNode2.parent.ruleNum and treeNode1.repeatIndex==treeNode2.repeatIndex:
    if equivalentNodes(treeNode1.parent, treeNode2.parent):
      return True
  return False

#seems useless  
def flattenTreeNode(treeNode, flatChildrenList):
  for child in treeNode.children:
    if child.token!="XXXXX" and child.token!="XX":
      flatChildrenList.append(child)
    elif child.token=="XXXXX":
      flattenTreeNode(child, flatChildrenList) 

def fileCleaner():
  fp=open_file("op/6.sankoff-valid.txt", "w")
  fp.close()
  fp=open_file("op/5.sankoff-equivalence-fail.txt", "w")
  fp.close()
  fp=open_file("op/4.sankoff-discard.txt", "w")
  fp.close()
  # fp=open_file("op/3.joshi-valid.txt", "w")
  # fp.close()
  #fp=open_file("logs.txt", "w")
  #fp.close()
	  
def fillHindiRuleNums(treeNode):
  treeNode.ruleNum=treeNode.counterpart.ruleNum
  treeNode.repeatIndex=treeNode.counterpart.repeatIndex
  for child in treeNode.children:
    fillHindiRuleNums(child)

def findRank(child, grammar, ruleNum, language):

  for rhsNt in grammar[ruleNum].rhs:
    # print rhsNt.nonTerminal, child.label, str(rhsNt.index), str(child.repeatIndex)
    if(rhsNt.nonTerminal==child.label and rhsNt.index==child.repeatIndex):
      if language=="English":
        # print "------"
        return rhsNt.engRank
      if language=="Hindi":
        # print "------"
        return rhsNt.hinRank
  
  return -1 	

#seems useless
def getTokenNumber(treeNode):
  return treeNode.tokenNum  
  
def grammarPrinter(grammar):
  for rule in grammar:
    print("(" + str(grammar.index(rule)) + ")" + rule.lhs.nonTerminal + "--->")
    for el in rule.rhs:
      print(el.nonTerminal + el.index + el.engRank + el.hinRank)
  
def highToken(treeNode):
  if treeNode.token!="XXXXX":
    return treeNode.tokenNum
  else:
    return max([highToken(x) for x in treeNode.children])

#seems useless
def insertIndex(root, hinTokenList):
  if root.children==[]:
    return hinTokenList.index(root)
  else:
    return insertIndex(root.children[0], hinTokenList)	
	
def lowToken(treeNode):      
  if treeNode.token!="XXXXX":
    return treeNode.tokenNum
  else:
    return min([lowToken(x) for x in treeNode.children])	

#seems useless
def lowTokenComparator(treeNode1, treeNode2):
  if lowToken(treeNode1)<lowToken(treeNode2):
    return -1
  if lowToken(treeNode1)>lowToken(treeNode2):
    return 1
  return 0
  
def popLang(root, lang):
  root.language=lang
  for child in root.children:
    popLang(child, lang)

#seems useless
def printRuleFiveFail(treeNode):

  if treeNode.token!="XXXXX":
    fp=open_file("op/5.sankoff-equivalence-fail.txt", "a")
    if treeNode.language=="English":
      fp.write(treeNode.token+" ")
    else:
      fp.write(treeNode.counterpart.token+" ")
    fp.close()
    return

  if treeNode.eq=="sank":
    fp=open_file("op/5.sankoff-equivalence-fail.txt", "a")
    fp.write("( ")
    fp.close()

  for child in treeNode.children:
    printRuleFiveFail(child)

  if treeNode.eq=="sank":
    fp=open_file("op/5.sankoff-equivalence-fail.txt", "a")
    fp.write(") ")
    fp.close()  
   
	
def purgeLabels(root):
  if root.token=="XXXXX":
    root.language=""
  else:
    if root.language=="EnglishClash":
      root.language="English"
    elif root.language=="HindiClash":
      root.language="Hindi"

  for child in root.children:
    purgeLabels(child)  	
	
def setParents(treeNode):
  for child in treeNode.children:
    child.parent=treeNode
    setParents(child)	
    
def treatNullMorphemes(root):
  if root.token=="$":
    root.token=""
  for child in root.children:
    treatNullMorphemes(child)

#seems useless
def trimEmptyParents(root):
  for child in root.children:
    if child.token=="XXXXX" and child.children==[]:
      root.children.remove(child)
    else:
      trimEmptyParents(child)

def updateRepeatIndexEnglish(treeNode):

  for child in treeNode.children:
    repeatIndex=0
    for iterator in range(treeNode.children.index(child)):
      if treeNode.children[iterator].label==child.label:
        repeatIndex=repeatIndex+1
    child.repeatIndex=repeatIndex
    updateRepeatIndexEnglish(child)

def updateRepeatIndexHindi(treeNode):
  
  for child in treeNode.children:
    child.repeatIndex=child.counterpart.repeatIndex
    updateRepeatIndexHindi(child)
	
def usedUp(checkNode, bitList):

  if checkNode.token!="XXXXX":
    if bitList[checkNode.tokenNum]==1:
      return True
    else:
      return False

  else:
    cond=True
    for child in checkNode.children:
      cond=(cond and usedUp(child, bitList))
    return cond

def useful(treeNode):
  if treeNode.token=="XX":
    return False
  return True
  
  
    